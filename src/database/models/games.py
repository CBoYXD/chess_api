from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import BIGINT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import Base, TimestampMixin


class Game(Base, TimestampMixin):
	__tablename__ = "games"
	game_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
	room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"))
	winner_user_id: Mapped[Optional[int]] = mapped_column(BIGINT, nullable=True)
	current_turn_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
	fen: Mapped[str] = mapped_column(
		String(100),
		server_default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
	)
	white_piece_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
	black_piece_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
