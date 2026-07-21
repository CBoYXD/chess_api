from datetime import datetime
from logging import getLogger
from typing import Optional

from fastapi import WebSocket
from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.games import Game
from src.database.models.room_members import RoomMember
from src.database.models.rooms import Room, RoomStatus
from src.database.models.users import User
from src.database.repo.requests import RequestsRepo

from ..exceptions import UserDisconnectWin

logger = getLogger("play")


class WaitEventValidator:
	def __init__(
		self,
		websocket: WebSocket,
		redis: Redis,
		pubsub: PubSub,
		user: User,
		room: Room,
		game: Game,
		room_member: RoomMember,
	):
		self.session: Optional[AsyncSession] = None
		self.repo: Optional[RequestsRepo] = None
		self.websocket = websocket
		self.redis = redis
		self.pubsub = pubsub
		self.user = user
		self.room = room
		self.game = game
		self.room_member = room_member
		self.disconnected_timeout = 30
		self.disconnect_user_time: Optional[datetime] = None
		self.max_num_players = 2
		self.send_connect_timestamp = False

	async def __call__(self, session: AsyncSession) -> bool:
		self.set_session(session)
		if await self.check_redis_connection():
			if self.disconnect_user_time is not None:
				self.disconnect_user_time = None
			if not self.send_connect_timestamp:
				# Множимо на тисячу, бо js сприймає тільки в мілісекундах, а python дає в секундах
				timestamp_now = int(datetime.now().timestamp()) * 1000
				await self.websocket.send_json({"type": "connect_user", "data": timestamp_now})
				self.send_connect_timestamp = True
			return True
		else:
			if self.disconnect_user_time is None:
				self.disconnect_user_time = datetime.now()
				await self.websocket.send_json({"type": "wait", "data": None})
				return False
			else:
				if (datetime.now() - self.disconnect_user_time).seconds >= self.disconnected_timeout:
					await self.handle_user_disconnected()
					raise UserDisconnectWin()
				else:
					await self.websocket.send_json({"type": "wait", "data": None})
					return False

	async def check_redis_connection(self) -> bool:
		self.room = await self.session.get_one(Room, self.room.room_id)
		# Якщо той хто зробив останній крок вже закрив групу, але не встиг зайти в RedisEventValidator до того,
		# як опонент вийде з кімнати, додамо таку перевірку, щоб останнє ітерація пройшла.
		# Теоретично проблем не має бути, бо повсюди де я ставлю закриту руму, рейзиться помилка для завершення.
		# Але якщо будуть якісь проблеми, подумати над іншим способом. #FIXME
		if self.room.status != RoomStatus.CLOSED:
			num_of_players = await self.repo.room_members.get_active_num_players(self.room.room_id)
			logger.info(f"Number of players in room: {self.room.room_id} is {num_of_players}")
			return num_of_players == self.max_num_players
		else:
			return True

	async def handle_user_disconnected(self):
		self.room.status = RoomStatus.CLOSED
		self.room_member.in_game = False
		await self.session.merge(self.room)
		await self.session.merge(self.room_member)
		await self.session.commit()
		await self.websocket.send_json({"type": "game_over", "data": {"reason": "user_disconnected"}})
		await self.pubsub.close()

	def set_session(self, session: AsyncSession):
		self.session = session
		self.repo = RequestsRepo(session)
