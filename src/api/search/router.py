from logging import getLogger

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.database.setup import sessionmaker
from src.api.utils import get_user
from src.database.models.search import SearchType
from src.database.repo.requests import RequestsRepo

from .dependencies import expectant, get_user_role, seeker
from .utils import on_disconnect

logger = getLogger("search")
search_router = APIRouter(prefix="/search")


@search_router.websocket("")
async def search(
	websocket: WebSocket,
	user_id: int,
	timeout: float = 1.0,
	game_name: str = "Online Game",
):
	try:
		async with sessionmaker() as session:
			repo = RequestsRepo(session)
			user = await get_user(repo, user_id)
			await websocket.accept()
			logger.info(f"User-{user_id} in search with timeout {timeout}")
			# Дізнаємось яка кількість типів пошуку є в таблиці.
			# Далі ідея буде за принципом "світлофора" (підказали назву)
			# Ми будемо отримувати юзерів по рейтингу,
			# і в залежності від кількості якогось пошукового типу
			# будемо вибирати їм свій пошуковий тип.
			# А далі, в залежності від типу будуть виконувати якісь дії.
			# Логічно, що з типом "Wait" юзер буде чекати,
			# поки інший суперник з типом "SEEK" не запише йому в таблицю айді кімнати.
			# Після цього як він отримає цей айді, він поверне його з ендпоінта,
			# додавши перед цим себе в "RoomMember", а також видалить свій запис в "Search".
			# Суперник з типом "SEEK", в свою чергу,
			# створить кімнату, гру, і також додасть себе в "RoomMember", і видалить свій запис в "Search".
			# Також варто зазначити, що більшість операцій з таблицею проходить через search_id,
			# тому проблем з одночасними іграми від 1 юзера не мало б бути. TODO: Перевірити

			role = await get_user_role(repo, user)
			logger.info(f"User-{user_id} role {role}")

			search = await repo.search.create_record(user_id, user.rank, role)
			logger.info(f"User-{user_id} search_id {search.search_id}")

		if role == SearchType.SEEK:
			data = await seeker(websocket, user, search, game_name, timeout)

		elif role == SearchType.WAIT:
			data = await expectant(websocket, search, user_id, timeout)

		await websocket.send_json(data.model_dump())
		await websocket.close()

	except WebSocketDisconnect:
		async with sessionmaker() as session:
			await on_disconnect(session, search.search_id)
		logger.info(f"User-{user_id} breaks search websocket!")
