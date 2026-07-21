from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin


class RoomMemberRole(Enum):
	PLAYER = "player"
	SPECTATOR = "spectator"


class RoomMember(Base, TimestampMixin):
	__tablename__ = "room_members"
	room_member_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
	room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"))
	in_game: Mapped[bool] = mapped_column(default=False)
	role: Mapped[RoomMemberRole] = mapped_column(
		SqlEnum(RoomMemberRole),
		nullable=False,
		server_default=RoomMemberRole.SPECTATOR.name,
	)

	# Define relationships
	user = relationship("User", back_populates="room_members")
	room = relationship("Room", back_populates="room_members")

	def __repr__(self):
		return f"<RoomMember user_id={self.user_id} room_id={self.room_id} role={self.role}>"
