import asyncio
from logging import getLogger

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio.client import Redis

from src.api.config import get_redis
from src.database.setup import sessionmaker
from src.api.utils import get_user
from src.database.repo.requests import RequestsRepo

from . import utils
from .dependencies import redis_listener, websocket_sender
from .event_validators import (
	DisconnectEventValidator,
	RedisEventValidator,
	WaitEventValidator,
	WebSocketEventValidator,
)
from .exceptions import GameOver, UserDisconnectWin
from .rating import calculate_rating, Rating

play_router = APIRouter(prefix="/play")
logger = getLogger("play")


@play_router.websocket("")
async def play_room(
	user_id: int,
	room_id: int,
	websocket: WebSocket,
	redis: Redis = Depends(get_redis),
):
	async with sessionmaker() as session:
		repo = RequestsRepo(session)

		user = await get_user(repo, user_id)
		room_member = await utils.get_room_member(repo, user_id, room_id)
		room = await utils.get_room(repo, room_id)
		game = await repo.games.get_game_by_room_id(room_id)

		pubsub = redis.pubsub()
		await websocket.accept()
		await utils.setup_game(session, pubsub, room, room_member)

		# opponent_user = await utils.get_opponent_user(repo, game, user_id)
	
	# rating = calculate_rating(user, opponent_user)
	rating = Rating(on_win=float(user.rank), on_draw=float(user.rank), on_lose=float(user.rank))
	wait_event_validator = WaitEventValidator(websocket, redis, pubsub, user, room, game, room_member)
	websocket_event_validator = WebSocketEventValidator(websocket, redis, user, room, game)
	redis_event_validator = RedisEventValidator(websocket, pubsub, user, room, game, room_member, rating)

	await websocket.send_json({"type": "init", "data": game.fen})
	try:
		lock = asyncio.Lock()
		await asyncio.gather(
			websocket_sender(lock, wait_event_validator, websocket_event_validator, websocket),
			redis_listener(lock, wait_event_validator, redis_event_validator, pubsub),
		)
	except WebSocketDisconnect:
		await pubsub.close()
		async with sessionmaker() as session:
			await utils.set_in_game_false(session, room_member)
			disconnect_event_validator = DisconnectEventValidator(session, redis, room)
			while await disconnect_event_validator():
				await asyncio.sleep(0.5)
			logger.info(f"User-{user_id} closed room-{room_id}, after disconnecting")
	except UserDisconnectWin:
		logger.info(f"User-{user_id} win, beacause opponent has been disconnected")
	except GameOver:
		pass
	logger.info(f"User-{user_id} has been disconnected from room-{room_id}")
