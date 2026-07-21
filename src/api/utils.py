from fastapi import WebSocketException, status

from src.database.models import Room, RoomMember, User
from src.database.repo.requests import RequestsRepo


async def get_user(repo: RequestsRepo, user_id: int) -> User:
	user = await repo.users.get_user_by_id(user_id)
	if user is None:
		raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
	return user


async def get_room_member(repo: RequestsRepo, user_id: int, room_id: int) -> RoomMember:
	room_member = await repo.room_members.get_room_member(user_id, room_id)
	if not room_member:
		raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User don't exist in this room")
	return room_member


async def get_room(repo: RequestsRepo, room_id: int) -> Room:
	room = await repo.rooms.get_room_by_id(room_id)
	if room is None:
		raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room not found")
	return room
