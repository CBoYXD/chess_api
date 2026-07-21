from typing import Optional

from sqlalchemy import insert, select

from src.database.models.games import Game
from src.database.repo.base import BaseRepo


class GameRepo(BaseRepo):
	async def create_game(
		self,
		room_id: int,
		white_piece_user_id: int,
		black_piece_user_id: int,
	) -> Game:
		insert_stmt = (
			insert(Game)
			.values(
				room_id=room_id,
				current_turn_user_id=white_piece_user_id,
				white_piece_user_id=white_piece_user_id,
				black_piece_user_id=black_piece_user_id,
			)
			.returning(Game)
		)
		result = await self.session.execute(insert_stmt)
		await self.session.commit()
		return result.scalar_one()

	async def get_game_by_room_id(self, room_id: int) -> Game:
		statement = select(Game).where(Game.room_id == room_id)
		result = await self.session.execute(statement)
		return result.scalar_one()

	async def nullable_get_game_by_room_id(self, room_id: int) -> Optional[Game]:
		statement = select(Game).where(Game.room_id == room_id)
		result = await self.session.execute(statement)
		return result.scalar_one_or_none()
