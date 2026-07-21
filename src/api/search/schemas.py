from typing import Literal

from pydantic import BaseModel


class SearchResult(BaseModel):
	room_id: int
	color: Literal["white", "black"]
	opponent_user_id: int
