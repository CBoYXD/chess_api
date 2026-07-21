from fastapi import WebSocketException, status

from src.api.utils import get_room as util_get_room
from src.database.models.room_members import RoomMemberRole
from src.database.models.rooms import RoomStatus, Room
from src.database.repo.requests import RequestsRepo


async def get_room(repo: RequestsRepo, room_id: int) -> Room:
    room = await util_get_room(repo, room_id)
    if room.status != RoomStatus.NEW:
        raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Players already join")
    return room


async def check_player_num(repo: RequestsRepo, room_id: int) -> None:
    players = await repo.room_members.get_room_members(room_id, RoomMemberRole.PLAYER)

    if len(players) == 2:
        raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Already two players in room")
