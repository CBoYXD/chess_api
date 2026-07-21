from enum import Enum

from sqlalchemy import Boolean
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin


class RoomStatus(Enum):
	NEW = "new"
	ACTIVE = "active"
	CLOSED = "closed"


class Room(Base, TimestampMixin):
	__tablename__ = "rooms"
	room_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	admin_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
	name: Mapped[str] = mapped_column(String(100))
	status: Mapped[RoomStatus] = mapped_column(SqlEnum(RoomStatus), nullable=False, server_default=RoomStatus.NEW.name)
	private: Mapped[bool] = mapped_column(Boolean, server_default=false())
	room_members = relationship("RoomMember", back_populates="room")

	def __repr__(self):
		return f"<Room {self.room_id} {self.name} ({self.status})>"
