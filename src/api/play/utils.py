from fastapi import WebSocketException, status
from redis.asyncio.client import PubSub
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.utils import get_room_member as util_get_room_member, \
    get_room as util_get_room
from src.database.models import Room, RoomMember
from src.database.models.room_members import RoomMemberRole
from src.database.models.rooms import RoomStatus
from src.database.models.games import Game
from src.database.models.users import User
from src.database.repo.requests import RequestsRepo


async def get_room_member(repo: RequestsRepo, user_id: int, room_id: int) -> RoomMember:
	room_member = await util_get_room_member(repo, user_id, room_id)
	if room_member.role != RoomMemberRole.PLAYER:
		raise WebSocketException(
			code=status.WS_1008_POLICY_VIOLATION,
			reason="Don't have permission to play in this room",
		)
	return room_member


async def get_room(repo: RequestsRepo, room_id: int) -> Room:
	room = await util_get_room(repo, room_id)
	if room.status == RoomStatus.CLOSED:
		raise WebSocketException(
			code=status.WS_1008_POLICY_VIOLATION,
			reason="Room already closed",
		) 
	return room


async def setup_game(session: AsyncSession, pubsub: PubSub, room: Room, room_member: RoomMember):
	await pubsub.subscribe(room.room_id)

	room.status = RoomStatus.ACTIVE
	room_member.in_game = True

	await session.merge(room)
	await session.merge(room_member)
	await session.commit()


async def set_in_game_false(session: AsyncSession, room_member: RoomMember) -> None:
	room_member.in_game = False
	await session.merge(room_member)
	await session.commit()


async def get_opponent_user(repo: RequestsRepo, game: Game, user_id: int) -> User:
    opponent_user_id = ({game.white_piece_user_id, game.black_piece_user_id} - {user_id}).pop()
    opponent_user = await repo.users.not_nullable_get_user_by_id(opponent_user_id)
    return opponent_user
