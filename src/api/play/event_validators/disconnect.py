from datetime import datetime
from logging import getLogger
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.rooms import Room, RoomStatus
from src.database.repo.requests import RequestsRepo

logger = getLogger("play")


class DisconnectEventValidator:
	def __init__(
		self,
		session: AsyncSession,
		redis: Redis,
		room: Room,
	):
		self.session = session
		self.repo = RequestsRepo(session)
		self.redis = redis
		self.room = room
		self.disconnect_user_time: Optional[datetime] = None
		self.disconnect_user_timeout = 30

	async def __call__(self):
		"""
		Повертає True, якщо кількість гравців більше нуля,
		або якщо всі гравці відключені більше ніж на 30 секунд
		"""
		if await self.check_redis_connection():
			if not self.disconnect_user_time:
				self.disconnect_user_time = datetime.now()
				return True
			else:
				if (datetime.now() - self.disconnect_user_time).seconds >= self.disconnect_user_timeout:
					self.room.status = RoomStatus.CLOSED
					await self.session.merge(self.room)
					await self.session.commit()
					return False
				else:
					return True
		return False

	async def check_redis_connection(self) -> bool:
		num_of_players = await self.repo.room_members.get_active_num_players(self.room.room_id)
		logger.info(f"Number of players in room: {self.room.room_id} is {num_of_players}")
		return num_of_players == 0
