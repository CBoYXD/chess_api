from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.setup import get_session
from src.database.repo.requests import RequestsRepo

from .schemas import GeneralStats

stats_router = APIRouter(prefix="/stats")


@stats_router.get("/all")
async def get_all_stats(session: AsyncSession = Depends(get_session)) -> GeneralStats:
	repo = RequestsRepo(session)
	return GeneralStats(active_users=await repo.users.get_all_active_users_num())
