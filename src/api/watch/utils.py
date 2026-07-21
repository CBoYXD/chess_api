from fastapi import WebSocketException, status
from redis.asyncio.client import PubSub
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.utils import get_room_member as util_get_room_member
from src.database.models import RoomMember
from src.database.models.room_members import RoomMemberRole
from src.database.repo.requests import RequestsRepo


async def get_room_member(repo: RequestsRepo, user_id: int, room_id: int) -> RoomMember:
	room_member = await util_get_room_member(repo, user_id, room_id)
	if room_member.role != RoomMemberRole.SPECTATOR:
		raise WebSocketException(
			code=status.WS_1008_POLICY_VIOLATION,
			reason="Don't have permission to play in this room",
		)
	return room_member


async def setup_game(session: AsyncSession, pubsub: PubSub, room_id: int, room_member: RoomMember):
	await pubsub.subscribe(room_id)

	room_member.in_game = True

	await session.merge(room_member)
	await session.commit()


async def on_disconnect(session: AsyncSession, room_member: RoomMember):
	room_member.in_game = False
	await session.merge(room_member)
	await session.commit()
