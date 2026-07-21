from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import BIGINT
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import Base, TimestampMixin


class SearchType(Enum):
	SEEK = "seek"
	WAIT = "wait"


class Search(Base, TimestampMixin):
	__tablename__ = "search"

	search_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
	rank: Mapped[int] = mapped_column(BIGINT, default=100)
	room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.room_id"), nullable=True)
	search_type: Mapped[SearchType] = mapped_column(SqlEnum(SearchType), nullable=False)
