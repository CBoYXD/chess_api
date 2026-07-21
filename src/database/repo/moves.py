from uuid import UUID

from sqlalchemy import insert

from src.database.models.moves import Move
from src.database.repo.base import BaseRepo


class MoveRepo(BaseRepo):
	async def create_move(self, user_id: int, game_id: UUID, fen: str) -> Move:
		insert_stmt = (
			insert(Move)
			.values(
				user_id=user_id,
				game_id=game_id,
				move=fen,
			)
			.returning(Move)
		)
		result = await self.session.execute(insert_stmt)
		await self.session.commit()
		return result.scalar_one()
