from pydantic import BaseModel


class CreateRoom(BaseModel):
	user_id: int
	name: str
	private: bool = False


class AddSpectator(BaseModel):
	user_id: int
	room_id: int
