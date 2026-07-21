from datetime import date
from typing import Optional

from sqlalchemy import func, select, text, true, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from src.database.models import User
from src.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
	async def get_or_create_user(
		self,
		user_id: int,
		full_name: str,
		username: Optional[str] = None,
	):
		"""
		Creates or updates a new user in the database and returns the user object.

		:param user_id: The user's ID.
		:param full_name: The user's full name.
		:param username: The user's username. It's an optional parameter.
		:return: User object, None if there was an error while making a transaction.

		Parameters
		----------
		banned
		"""

		insert_stmt = (
			insert(User)
			.values(
				user_id=user_id,
				username=username,
				full_name=full_name,
			)
			.on_conflict_do_update(
				index_elements=[User.user_id],
				set_=dict(
					username=username,
					full_name=full_name,
				),
			)
			.returning(User)
		)
		result = await self.session.execute(insert_stmt)
		await self.session.commit()
		return result.scalar_one()

	async def get_all_chat_ids(self):
		"""
		Returns all chat_ids from the User table.

		:return: A list of chat_ids.
		"""
		statement = select(User.user_id)
		result = await self.session.execute(statement)
		return [row[0] for row in result.fetchall()]

	async def get_all_users(self):
		"""
		Returns all users from the User table.

		:return: A list of User objects.
		"""
		statement = select(User)
		result = await self.session.execute(statement)
		return result.scalars().all()

	async def get_user_by_id(self, user_id: int) -> Optional[User]:
		"""
		Returns a user from the User table by ID.

		:param user_id: The user's ID.
		:return: User object, None if there was an error while making a transaction.
		"""
		statement = select(User).where(User.user_id == user_id)
		result = await self.session.execute(statement)
		return result.scalar_one_or_none()

	async def not_nullable_get_user_by_id(self, user_id: int) -> User:
		"""
		Returns a user from the User table by ID.

		:param user_id: The user's ID.
		:return: User object, None if there was an error while making a transaction.
		"""

		result = await self.get_user_by_id(user_id)
		if result is None:
			raise NoResultFound("User not found")
		return result

	async def get_users_by_date(self, today_date: date):
		"""
		Returns all users from the User table that were created on the specified date.

		:param today_date: Today date
		:return: A list of User objects.
		"""
		statement = select(User).where(func.date(User.created_at) == today_date)
		result = await self.session.execute(statement)
		return result.scalars().all()

	async def get_users_by_24h(self):
		"""
		Returns all users from the User table that were created in the last 24 hours.

		:return: A list of User objects.
		"""
		twenty_four_hours_ago = func.now() - text("interval '24 hours'")
		statement = select(User).where(User.created_at >= twenty_four_hours_ago)
		result = await self.session.execute(statement)
		return result.scalars().all()

	async def ban_or_unban_user(self, user_id: int, status: bool):
		"""
		Bans or unbans a user from the User table.

		:param user_id: The user's ID.
		:param status: The user's status.
		"""
		statement = update(User).where(User.user_id == user_id).values(banned=status)
		result = await self.session.execute(statement)
		await self.session.commit()

		return result.rowcount

	async def ban_or_unban_by_username(self, username: str, status: bool):
		"""
		Bans or unbans a user from the User table.

		:param username: The user's username.

		Parameters
		----------
		status
		"""
		statement = update(User).where(User.username == username).values(banned=status)
		await self.session.execute(statement)
		await self.session.commit()

	async def get_all_active_users_num(self) -> int:
		statement = select(User.user_id).where(User.active == true())
		result = await self.session.execute(statement)
		return len(result.scalars().all())
