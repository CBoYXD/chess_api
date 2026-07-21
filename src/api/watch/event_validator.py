from json import loads
from logging import getLogger

from fastapi import WebSocket
from redis.asyncio.client import PubSub
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.games import Game
from src.database.models.rooms import Room
from src.database.models.users import User
from src.database.repo.requests import RequestsRepo

logger = getLogger("watch")


class WatchEventValidator:
	def __init__(
		self,
		websocket: WebSocket,
		pubsub: PubSub,
		user: User,
		room: Room,
		game: Game,
	):
		self.websocket = websocket
		self.pubsub = pubsub
		self.user = user
		self.room = room
		self.game = game

	async def handle_events(self, session: AsyncSession, message: dict[str, bytes]) -> None:
		data = await self.deserialize_redis_message(message)
		self.set_session(session)
		if data["type"] == "move":
			await self.handle_move_event(data["data"]["move"])
		elif data["type"] == "game_over":
			await self.handle_game_over(data)
		self.remove_session()

	async def handle_move_event(self, move: str) -> None:
		await self.websocket.send_json({"type": "move", "data": move})

	async def handle_game_over(self, data: dict) -> None:
		await self.websocket.send_json(data)

	async def deserialize_redis_message(self, message: dict[str, bytes]) -> dict:
		return loads(message["data"].decode("utf-8"))

	def set_session(self, session):
		self.session = session
		self.repo = RequestsRepo(session)

	def remove_session(self):
		self.session = None
		self.repo = None
