import asyncio

from fastapi import WebSocket
from redis.asyncio.client import PubSub

from src.database.setup import sessionmaker

from .event_validators import (
	RedisEventValidator,
	WaitEventValidator,
	WebSocketEventValidator,
)


async def redis_listener(
	lock: asyncio.Lock,
	wait_event_validator: WaitEventValidator,
	redis_event_validator: RedisEventValidator,
	pubsub: PubSub,
	timeout: float = 0.25,
):
	while True:
		async with sessionmaker() as session:
			async with lock:
				check_connection = await wait_event_validator(session)

		if check_connection:
			message = await pubsub.get_message(ignore_subscribe_messages=True)
			if message:
				async with sessionmaker() as session:
					await redis_event_validator.handle_events(session, message)
		await asyncio.sleep(timeout)


async def websocket_sender(
	lock: asyncio.Lock,
	wait_event_validator: WaitEventValidator,
	websocket_event_validator: WebSocketEventValidator,
	websocket: WebSocket,
	timeout: float = 0.5,
):
	while True:
		async with sessionmaker() as session:
			async with lock:
				check_connection = await wait_event_validator(session)
		if check_connection:
			data = await websocket.receive_json()
			async with sessionmaker() as session:
				await websocket_event_validator.handle_events(session, data)
		await asyncio.sleep(timeout)
