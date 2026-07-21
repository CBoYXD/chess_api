from asyncio import sleep as asleep
from fastapi import WebSocket

from src.database.setup import sessionmaker
from src.database.repo.requests import RequestsRepo
from .event_validator import RoomWsEventValidator


async def start_game_if_already_player_in_room(
    repo: RequestsRepo, 
    websocket: WebSocket, 
    room_id: int, 
    user_id: int,
    timeout: float = 2
) -> None:
    
    while True:
        game = await repo.games.nullable_get_game_by_room_id(room_id)
        if game is not None:
            break
        await websocket.send_json({"wait": None})
        await asleep(timeout)
    
    my_color = "white" if game.white_piece_user_id == user_id else "black"
    await websocket.send_json({"type": "start_game", "data": my_color})
    await websocket.close()
    return


async def wait_for_second_player(
    websocket: WebSocket, 
    event_validator: RoomWsEventValidator,
    timeout: float = 2
) -> None:
    while True:
        async with sessionmaker() as session:
            connection = await event_validator(session)
            if connection:
                await websocket.close()
                break
        await asleep(timeout)
