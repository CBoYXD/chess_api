from json import dumps
from logging import getLogger
from typing import Literal

from fastapi import WebSocket
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.games import Game
from src.database.models.rooms import Room, RoomStatus
from src.database.models.users import User
from src.database.repo.requests import RequestsRepo

logger = getLogger("play")


class WebSocketEventValidator:
	def __init__(
		self,
		websocket: WebSocket,
		redis: Redis,
		user: User,
		room: Room,
		game: Game,
	):
		self.websocket = websocket
		self.redis = redis
		self.user = user
		self.room = room
		self.game = game

	async def handle_events(self, session: AsyncSession, data: dict) -> None:
		self.session = session
		self.repo = RequestsRepo(session)
		logger.info(f"Full data from user-{self.user.user_id}: {str(data)}")
		if data["type"] == "move":
			await self.handle_move_event(data["data"])
		elif data["type"] == "checkmate":
			await self.handle_checkmate_event(data["winner"])
		elif data["type"] == "draw":
			await self.handle_draw(data["detail"])

	async def handle_move_event(self, move: str) -> None:
		await self.redis.publish(
			self.room.room_id,
			dumps({"type": "move", "data": {"move": move, "user_id": self.user.user_id}}),
		)
		logger.info(f"Move from user-{self.user.user_id}: {move}")
		await self.repo.moves.create_move(self.user.user_id, self.game.game_id, move)
		self.game.fen = move
		await self.session.merge(self.game)
		await self.session.commit()

	async def handle_checkmate_event(self, winner: Literal["white", "black"]) -> None:
		if await self.__check_if_user_winner(winner):
			await self.redis.publish(
				self.room.room_id,
				dumps(
					{
						"type": "game_over",
						"data": {"reason": "checkmate", "winner": winner},
					}
				),
			)
			self.game.winner_user_id = self.user.user_id
			self.room.status = RoomStatus.CLOSED
			await self.session.merge(self.game)
			await self.session.merge(self.room)
			await self.session.commit()

	async def handle_draw(self, draw_type: str) -> None:
		await self.redis.publish(
			self.room.room_id,
			dumps({"type": "game_over", "data": {"reason": draw_type}}),
		)
		self.room.status = RoomStatus.CLOSED
		await self.session.merge(self.room)
		await self.session.commit()

	async def __check_if_user_winner(self, winner: Literal["white", "black"]) -> bool:
		if winner == "white":
			return self.user.user_id == self.game.white_piece_user_id
		else:
			return self.user.user_id == self.game.black_piece_user_id
