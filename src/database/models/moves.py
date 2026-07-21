from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import Base, TimestampMixin


class Move(Base, TimestampMixin):
	__tablename__ = "moves"
	move_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
	game_id: Mapped[int] = mapped_column(ForeignKey("games.game_id"))
	move: Mapped[str] = mapped_column(String(100))
