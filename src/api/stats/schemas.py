from pydantic import BaseModel


class GeneralStats(BaseModel):
	active_users: int
