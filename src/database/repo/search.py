from typing import Optional
from uuid import UUID

from sqlalchemy import delete, insert, select, update

from src.database.models import Search
from src.database.models.search import SearchType
from src.database.repo.base import BaseRepo


class SearchRepo(BaseRepo):
	async def create_record(self, user_id: int, rank: int, role: SearchType) -> Search:
		create_statement = insert(Search).values(user_id=user_id, rank=rank, search_type=role).returning(Search)
		result = await self.session.execute(create_statement)
		await self.session.commit()
		return result.scalar_one()

	async def get_opponent_data(self, user_id: int, rank: int, deviation: int = 50) -> Optional[dict]:
		search_statement = (
			select(Search.user_id, Search.search_id)
			.where(
				Search.user_id != user_id,  # Exclude the user itself
				Search.rank.between(rank - deviation, rank + deviation),
				Search.search_type == SearchType.WAIT,
				Search.room_id.is_(None),
			)
			.order_by(Search.created_at)
		)
		result = await self.session.execute(search_statement)
		users = result.mappings().all()
		if bool(users):
			return dict(users[0])
		return None

	async def get_search_type_by_rank(self, rank: int, deviation: int = 50) -> list[dict]:
		search_statement = (
			select(Search.user_id, Search.search_type)
			.where(
				Search.rank.between(rank - deviation, rank + deviation),  # TODO: Потім тут буде формула
				Search.room_id.is_(None),
			)
			.order_by(Search.created_at)
		)
		result = await self.session.execute(search_statement)
		return result.mappings().all()

	async def get_room_id(self, search_id: int) -> Optional[int]:
		search_statement = select(Search.room_id).where(Search.search_id == search_id)
		result = await self.session.execute(search_statement)
		return result.scalar_one_or_none()

	async def update_room_id(self, search_id: UUID, id: int) -> int:
		update_statement = (
			update(Search)
			.where(Search.search_id == search_id, Search.room_id.is_(None))
			.values(room_id=id)
			.returning(Search.room_id)
		)
		result = await self.session.execute(update_statement)
		await self.session.commit()
		return result.scalar_one()

	async def delete_record(self, search_id: UUID) -> None:
		delete_statement = delete(Search).where(Search.search_id == search_id)
		await self.session.execute(delete_statement)
		await self.session.commit()
