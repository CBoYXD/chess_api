from datetime import datetime
from typing import Optional

from sqlalchemy import BIGINT, Boolean, DateTime, String, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TableNameMixin, TimestampMixin


class User(Base, TimestampMixin, TableNameMixin):
	__tablename__ = "users"
	user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
	username: Mapped[Optional[str]] = mapped_column(String(128))
	full_name: Mapped[str] = mapped_column(String(128))
	rank: Mapped[int] = mapped_column(BIGINT, default=100)
	active: Mapped[bool] = mapped_column(Boolean, server_default=true())
	created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
	room_members = relationship("RoomMember", back_populates="user")

	def __repr__(self):
		return f"<User {self.user_id} {self.username} {self.full_name}>"
