from src.api.play import play_router
from src.api.room import room_router
from src.api.search import search_router
from src.api.stats import stats_router
from src.api.user import user_router
from src.api.watch import watch_router

routers = [
	room_router,
	search_router,
	user_router,
	stats_router,
	play_router,
	watch_router,
]
