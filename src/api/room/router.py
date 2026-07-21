from logging import getLogger
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.setup import get_session, sessionmaker
from src.api.utils import get_user
from src.database.repo.requests import RequestsRepo
from src.database.repo.room_members import RoomMemberRole

from .event_validator import RoomWsEventValidator
from .schemas import AddSpectator, CreateRoom
from .utils import check_player_num, get_room
from .dependencies import start_game_if_already_player_in_room, wait_for_second_player

room_router = APIRouter(prefix="/room")
logger = getLogger("room")


@room_router.websocket("/ws")
async def room_websocket(
	user_id: int,
	room_id: int,
	websocket: WebSocket
) -> None:
	async with sessionmaker() as session:
		repo = RequestsRepo(session)
		user = await get_user(repo, user_id)
		room = await get_room(repo, room_id)
		await check_player_num(repo, room_id)
		
		await websocket.accept()
  
		if room.admin_id != user_id:
			try:
				room_member = await repo.room_members.create_room_member(room_id, user_id, RoomMemberRole.PLAYER)
				return await start_game_if_already_player_in_room(repo, websocket, room_id, user_id)
			except WebSocketDisconnect:
				await repo.room_members.delete_room_member(room_member.room_member_id)
				return
		else:
			room_member = await repo.room_members.get_room_member(user_id, room_id)


	event_validator = RoomWsEventValidator(websocket, room, user)
	try:
		await wait_for_second_player(websocket, event_validator)
	except WebSocketDisconnect:
		await repo.room_members.delete_room_member(room_member.room_member_id)


@room_router.post("/create")
async def create_room(data: CreateRoom, session: AsyncSession = Depends(get_session)) -> int:
	try:
		repo = RequestsRepo(session)
		room = await repo.rooms.create_room(data.user_id, data.name, data.private)
		await repo.room_members.create_room_member(room.room_id, data.user_id, RoomMemberRole.PLAYER)
		return room.room_id
	except SQLAlchemyError:
		raise HTTPException(404, detail="User not found")



@room_router.patch("/add_spectator")
async def add_spectator_to_room(data: AddSpectator, session: AsyncSession = Depends(get_session)):
	try:
		repo = RequestsRepo(session)
		if not await repo.room_members.check_if_room_member_exist(
    		data.room_id, data.user_id, 
    		RoomMemberRole.SPECTATOR
    	):
			await repo.room_members.create_room_member(
    			data.room_id, data.user_id, 
    			RoomMemberRole.SPECTATOR
    		)
	except SQLAlchemyError:
		raise HTTPException(404, detail="User or room not found")
