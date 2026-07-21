from json import loads
from logging import getLogger

from fastapi import WebSocket
from redis.asyncio.client import PubSub
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.games import Game
from src.database.models.room_members import RoomMember
from src.database.models.rooms import Room
from src.database.models.users import User
from src.database.repo.requests import RequestsRepo

from ..exceptions import GameOver
from ..rating import Rating

logger = getLogger("play")


class RedisEventValidator:
	def __init__(
		self,
		websocket: WebSocket,
		pubsub: PubSub,
		user: User,
		room: Room,
		game: Game,
		room_member: RoomMember,
		rating: Rating
	):
		self.websocket = websocket
		self.pubsub = pubsub
		self.user = user
		self.room = room
		self.game = game
		self.room_member = room_member
		self.rating = rating

	async def handle_events(self, session: AsyncSession, message: dict[str, bytes]) -> None:
		self.session = session
		self.repo = RequestsRepo(session)
		data = await self.deserialize_redis_message(message)
		logger.info(f"Full redis data from user-{self.user.user_id}: {data}")
		if data["type"] == "move":
			if data["data"]["user_id"] != self.user.user_id:
				await self.handle_move_event(data["data"]["move"])
		elif data["type"] == "game_over":
			await self.handle_game_over(data)

	async def handle_move_event(self, move: str) -> None:
		self.game.current_turn_user_id = self.user.user_id
		await self.session.merge(self.game)
		await self.session.commit()
		await self.websocket.send_json({"type": "move", "data": move})

	async def handle_game_over(self, data: dict) -> None:
		self.room_member.in_game = False
		if data["data"]["reason"] == "draw_type":
			self.user.rank = self.rating.on_draw
		else:
			self.session.add(self.game)
			await self.session.refresh(self.game)
			if self.game.winner_user_id == self.user.user_id:
				self.user.rank = self.rating.on_win
			else:
				self.user.rank = self.rating.on_lose
		await self.session.merge(self.room_member)
		await self.session.merge(self.user)
		await self.session.commit()
		await self.websocket.send_json(data)
		raise GameOver()

	async def deserialize_redis_message(self, message: dict[str, bytes]) -> dict:
		return loads(message["data"].decode("utf-8"))
