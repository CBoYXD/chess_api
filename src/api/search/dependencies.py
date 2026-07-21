from asyncio import sleep as asleep
from logging import getLogger
from typing import Literal

from fastapi import WebSocket

from src.database.setup import sessionmaker
from src.database.models.room_members import RoomMemberRole
from src.database.models.search import Search, SearchType
from src.database.models.users import User
from src.database.repo.requests import RequestsRepo

from .schemas import SearchResult
from .utils import (
	get_color_for_expectant,
	get_opponent_user_id,
	get_room_id_for_expectant,
	get_users_colors,
)

logger = getLogger("search")


async def get_user_role(repo: RequestsRepo, user: User) -> SearchType:
	search_types_in_records = await repo.search.get_search_type_by_rank(user.rank)
	seek_search_type = [
		record["user_id"] for record in search_types_in_records if record["search_type"] == SearchType.SEEK
	]
	wait_search_type = [
		record["user_id"] for record in search_types_in_records if record["search_type"] == SearchType.WAIT
	]
	# Тобто, якщо кількість seekers буде більше ніж waiters,
	# і якщо всі seekers це один і той самий юзер(зайшов з різних вкладок на пошук гри),
	# то даємо йому теж роль SEEK
	logger.info(f"Amount of seekers: {len(seek_search_type)}")
	logger.info(f"Amount of waiters: {len(wait_search_type)}")
	if (not bool(seek_search_type)) and (not bool(wait_search_type)):
		return SearchType.SEEK
	elif seek_search_type.count(user.user_id) == len(seek_search_type):
		return SearchType.SEEK
	elif len(seek_search_type) >= len(wait_search_type):
		return SearchType.WAIT
	else:
		return SearchType.SEEK


async def seeker(websocket: WebSocket, user: User, search: Search, game_name: str, timeout: float) -> SearchResult:
	while True:
		async with sessionmaker() as session:
			repo = RequestsRepo(session)
			opponent_data = await repo.search.get_opponent_data(user.user_id, user.rank)
			if opponent_data is not None:
				opponent_user_id, opponent_search_id = (
					opponent_data["user_id"],
					opponent_data["search_id"],
				)
				logger.info(f"Opponent user id for user-{user.user_id} is {opponent_user_id}")
				room = await repo.rooms.create_room(user.user_id, game_name)
				updated_room_id = await repo.search.update_room_id(opponent_search_id, room.room_id)

				if room.room_id != updated_room_id:
					await repo.rooms.delete_room(room.room_id)
					continue

				logger.info(f"Created room id: {room.room_id}")
				await repo.room_members.create_room_member(room.room_id, user.user_id, RoomMemberRole.PLAYER)
				white_piece, black_piece = await get_users_colors(user.user_id, opponent_user_id)
				logger.info(f"White_piece: {white_piece}, Black_piece: {black_piece}")
				color: Literal["white", "black"] = "white" if white_piece == user.user_id else "black"
				await repo.games.create_game(room.room_id, white_piece, black_piece)
				await repo.search.delete_record(search.search_id)
				break
			else:
				await websocket.send_json({"wait": None})
		await asleep(timeout)

	return SearchResult(room_id=room.room_id, color=color, opponent_user_id=opponent_user_id)


async def expectant(websocket: WebSocket, search: Search, user_id: int, timeout: float) -> SearchResult:
	room_id = await get_room_id_for_expectant(websocket, user_id, search, timeout)
	color = await get_color_for_expectant(websocket, user_id, room_id, timeout)
	opponent_user_id = await get_opponent_user_id(websocket, user_id, room_id, timeout)

	return SearchResult(room_id=room_id, color=color, opponent_user_id=opponent_user_id)
