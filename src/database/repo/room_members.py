from typing import Optional

from sqlalchemy import delete, insert, select, true

from src.database.models.room_members import RoomMember, RoomMemberRole
from src.database.repo.base import BaseRepo
from uuid import UUID


class RoomMemberRepo(BaseRepo):
	async def create_room_member(self, room_id: int, user_id: int, role: RoomMemberRole) -> RoomMember:
		insert_stmt = (
			insert(RoomMember)
			.values(
				room_id=room_id,
				user_id=user_id,
				role=role,
			)
			.returning(RoomMember)
		)
		result = await self.session.execute(insert_stmt)
		await self.session.commit()
		return result.scalar_one()

	async def check_if_room_member_exist(self, room_id: int, user_id: int, role: RoomMemberRole) -> bool:
		stmt = select(1).where(
      		RoomMember.room_id == room_id, 
        	RoomMember.user_id == user_id, 
        	RoomMember.role == role
        )
		result = await self.session.execute(stmt)
		return bool(result.first())

	async def get_room_members(self, room_id: int, role: RoomMemberRole) -> list[int]:
		stmt = select(RoomMember.user_id).where(RoomMember.role == role, RoomMember.room_id == room_id)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def get_room_member(self, user_id: int, room_id: int) -> Optional[RoomMember]:
		stmt = select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def delete_room_members(self, room_id: int) -> None:
		stmt = delete(RoomMember).where(RoomMember.room_id == room_id)
		await self.session.execute(stmt)
		await self.session.commit()

	async def delete_room_member(self, room_member_id: UUID) -> None:
		stmt = delete(RoomMember).where(RoomMember.room_member_id == room_member_id)
		await self.session.execute(stmt)
		await self.session.commit()

	async def get_active_num_players(self, room_id: int) -> int:
		stmt = select(1).where(
			RoomMember.room_id == room_id,
			RoomMember.role == RoomMemberRole.PLAYER,
			RoomMember.in_game == true(),
		)
		result = await self.session.execute(stmt)
		return len(result.scalars().all())
