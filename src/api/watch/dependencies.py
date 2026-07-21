from asyncio import sleep

from redis.asyncio.client import PubSub

from src.database.setup import sessionmaker

from .event_validator import WatchEventValidator


async def spectator_watch_game(watch_event_validator: WatchEventValidator, pubsub: PubSub, timeout: float = 0.5):
	while True:
		message = await pubsub.get_message(ignore_subscribe_messages=True)
		if message:
			async with sessionmaker() as session:
				await watch_event_validator.handle_events(session, message)
		await sleep(timeout)
