from asyncio import sleep as asleep
from logging import getLogger
from random import choice
from typing import Literal
from uuid import UUID

from fastapi import WebSocket
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.setup import sessionmaker
from src.database.models.room_members import RoomMemberRole
from src.database.models.search import Search
from src.database.repo.requests import RequestsRepo

logger = getLogger("search")


async def get_users_colors(user_id: int, opponent_user_id) -> tuple[int, int]:
	ids = [user_id, opponent_user_id]
	white_piece = choice(ids)
	ids.remove(white_piece)
	black_piece = ids[0]
	return white_piece, black_piece


async def get_room_id_for_expectant(websocket: WebSocket, user_id: int, search: Search, timeout: float) -> int:
	while True:
		async with sessionmaker() as session:
			repo = RequestsRepo(session)
			room_id = await repo.search.get_room_id(search.search_id)
			if room_id is not None:
				logger.info(f"Room id from seeker: {room_id}")
				await repo.room_members.create_room_member(room_id, user_id, RoomMemberRole.PLAYER)
				await repo.search.delete_record(search.search_id)
				break
			else:
				await websocket.send_json({"wait": None})
		await asleep(timeout)
	return room_id


async def get_color_for_expectant(
	websocket: WebSocket, user_id: int, room_id: int, timeout: float
) -> Literal["white", "black"]:
	while True:
		async with sessionmaker() as session:
			try:
				repo = RequestsRepo(session)
				game = await repo.games.get_game_by_room_id(room_id)
				color: Literal["white", "black"] = "white" if game.white_piece_user_id == user_id else "black"
				break
			except NoResultFound:
				await websocket.send_json({"wait": None})
		await asleep(timeout)
	return color


async def get_opponent_user_id(websocket: WebSocket, user_id: int, room_id: int, timeout: float) -> int:
	while True:
		async with sessionmaker() as session:
			repo = RequestsRepo(session)
			opponent_user_id = await repo.rooms.get_opponent_by_room_id_and_user_id(room_id, user_id)
			if opponent_user_id is not None:
				break
			else:
				await websocket.send_json({"wait": None})
		await asleep(timeout)
	return opponent_user_id


async def on_disconnect(session: AsyncSession, search_id: UUID) -> None:
	try:
		repo = RequestsRepo(session)
		await repo.search.delete_record(search_id)
	except NameError:
		pass
