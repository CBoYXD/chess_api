from logging import getLogger

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio.client import Redis

from src.api.config import get_redis
from src.database.setup import sessionmaker
from src.api.utils import get_room, get_user
from src.database.repo.requests import RequestsRepo

from . import utils
from .dependencies import spectator_watch_game
from .event_validator import WatchEventValidator

watch_router = APIRouter(prefix="/watch")
logger = getLogger("watch")


@watch_router.websocket("")
async def watch_game(
	user_id: int,
	room_id: int,
	websocket: WebSocket,
	redis: Redis = Depends(get_redis),
):
	async with sessionmaker() as session:
		repo = RequestsRepo(session)

		user = await get_user(repo, user_id)
		room_member = await utils.get_room_member(repo, user_id, room_id)
		room = await get_room(repo, room_id)
		game = await repo.games.get_game_by_room_id(room_id)

		pubsub = redis.pubsub()
		await websocket.accept()

		await utils.setup_game(session, pubsub, room_id, room_member)

	await websocket.send_json(
		{
			"type": "start_watch",
			"data": {
				"fen": game.fen,
				"white_piece_user_id": game.white_piece_user_id,
				"black_piece_user_id": game.black_piece_user_id,
			},
		}
	)
	watch_event_validator = WatchEventValidator(websocket, pubsub, user, room, game)
	try:
		await spectator_watch_game(watch_event_validator, pubsub)
	except WebSocketDisconnect:
		logger.info(f"Viewer-{user_id} has been disconnected from room-{room_id}")
		async with sessionmaker() as session:
			await utils.on_disconnect(session, room_member)
