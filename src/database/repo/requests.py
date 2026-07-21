from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repo.games import GameRepo
from src.database.repo.moves import MoveRepo
from src.database.repo.room_members import RoomMemberRepo
from src.database.repo.rooms import RoomRepo
from src.database.repo.search import SearchRepo
from src.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
	"""
	Repository for handling database operations. This class holds all the repositories for the database models.

	You can add more repositories as properties to this class, so they will be easily accessible.
	"""

	session: AsyncSession

	@property
	def users(self) -> UserRepo:
		"""
		The User repository sessions are required to manage user operations.
		"""
		return UserRepo(self.session)

	@property
	def games(self) -> GameRepo:
		"""
		The User repository sessions are required to manage user operations.
		"""
		return GameRepo(self.session)

	@property
	def room_members(self) -> RoomMemberRepo:
		"""
		The User repository sessions are required to manage user operations.
		"""
		return RoomMemberRepo(self.session)

	@property
	def rooms(self) -> RoomRepo:
		"""
		The User repository sessions are required to manage user operations.
		"""
		return RoomRepo(self.session)

	@property
	def search(self) -> SearchRepo:
		return SearchRepo(self.session)

	@property
	def moves(self) -> MoveRepo:
		return MoveRepo(self.session)
