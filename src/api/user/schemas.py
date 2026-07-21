from typing import Optional

from pydantic import BaseModel


class UpdateActive(BaseModel):
	user_id: int
	active: bool


class CreateUser(BaseModel):
	user_id: int
	fullname: str
	username: Optional[str] = None
