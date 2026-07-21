from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.setup import get_session
from src.database.repo.requests import RequestsRepo

from .schemas import CreateUser, UpdateActive

user_router = APIRouter(prefix="/user")


@user_router.post("/create")
async def create_user(
	data: CreateUser,
	session: AsyncSession = Depends(get_session),
):
	try:
		repo = RequestsRepo(session)
		user = await repo.users.get_or_create_user(data.user_id, data.fullname, data.username)
		return JSONResponse(status_code=200, content={"user_id": user.user_id})
	except Exception:
		raise HTTPException(status_code=500, detail="Failed to create user")


@user_router.patch("/active")
async def update_user_active(data: UpdateActive, session: AsyncSession = Depends(get_session)):
	repo = RequestsRepo(session)
	user = await repo.users.not_nullable_get_user_by_id(data.user_id)
	user.active = data.active
	await session.merge(user)
	await session.commit()


@user_router.get("/exists/{user_id}")
async def check_user_exists(
    user_id: int, 
    session: AsyncSession = Depends(get_session)
) -> dict[Literal["exists"], bool]:
	repo = RequestsRepo(session)
	user = await repo.users.get_user_by_id(user_id)
	return JSONResponse(status_code=200, content={"exists": user is not None})
