from logging import getLogger
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.search.utils import get_users_colors
from src.database.models.rooms import Room
from src.database.models.room_members import RoomMemberRole
from src.database.models.users import User
from src.database.repo.requests import RequestsRepo

logger = getLogger("room")


class RoomWsEventValidator:
    def __init__(self, websocket: WebSocket, room: Room, user: User):
        self.websocket = websocket
        self.room = room
        self.user = user
        
    async def __call__(self, session: AsyncSession) -> bool:
        self.session = session
        self.repo = RequestsRepo(session)
        players = await self.repo.room_members.get_room_members(self.room.room_id, RoomMemberRole.PLAYER)
        players_num = len(players)
        if players_num != 2:
            await self.websocket.send_json({"wait": None})
            return False
        else:
            opponent_user_id = (set(players) - {self.user.user_id}).pop()
            white_piece, black_piece = await get_users_colors(self.user.user_id, opponent_user_id)
            my_color = "white" if white_piece == self.user.user_id else "black"
            await self.repo.games.create_game(self.room.room_id, white_piece, black_piece)
            await self.websocket.send_json(
                {
                    "type": "start_game", 
                    "data": my_color
                }
            )
            return True
