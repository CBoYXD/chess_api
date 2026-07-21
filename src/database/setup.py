from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
	AsyncConnection,
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)

from src.api.config import config


engine = create_async_engine(config.db.construct_sqlalchemy_url(), echo=True)


class DatabaseSessionManager:
	def __init__(self, engine: AsyncEngine):
		self._engine = engine
		self._sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)

	async def close(self):
		await self._engine.dispose()

		self._sessionmaker = None
		self._engine = None

	@asynccontextmanager
	async def connect(self) -> AsyncIterator[AsyncConnection]:
		async with self._engine.begin() as connection:
			try:
				yield connection
			except Exception:
				await connection.rollback()
				raise

	@asynccontextmanager
	async def __call__(self) -> AsyncIterator[AsyncSession]:
		session = self._sessionmaker()

		try:
			yield session
		except Exception:
			await session.rollback()
			raise
		finally:
			await session.close()


sessionmaker = DatabaseSessionManager(engine)


async def get_session():
	async with sessionmaker() as session:
		yield session
