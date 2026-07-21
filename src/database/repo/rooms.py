from typing import Optional

from sqlalchemy import delete, insert, select

from src.database.models.room_members import RoomMember, RoomMemberRole
from src.database.models.rooms import Room
from src.database.repo.base import BaseRepo


class RoomRepo(BaseRepo):
	async def create_room(self, admin_id: int, name: str, private: bool = False) -> Room:
		insert_stmt = insert(Room).values(admin_id=admin_id, name=name, private=private).returning(Room)
		result = await self.session.execute(insert_stmt)
		await self.session.commit()
		return result.scalar_one()

	async def get_room_by_id(self, room_id: int) -> Optional[Room]:
		result = await self.session.get(Room, room_id)
		return result

	async def delete_room(self, room_id: int) -> None:
		delete_stmt = delete(Room).where(Room.room_id == room_id)
		await self.session.execute(delete_stmt)
		await self.session.commit()

	async def get_opponent_by_room_id_and_user_id(self, room_id: int, user_id: int) -> Optional[int]:
		stmt = (
			select(RoomMember.user_id)
			.join_from(Room, RoomMember, RoomMember.room_id == Room.room_id)
			.where(
				RoomMember.room_id == room_id,
				RoomMember.user_id != user_id,
				RoomMember.role == RoomMemberRole.PLAYER,
			)
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()
