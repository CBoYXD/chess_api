from dataclasses import dataclass

from environs import Env
from redis.asyncio import from_url as get_redis_from_url
from sqlalchemy import URL


@dataclass(frozen=True)
class DbConfig:
	host: str
	password: str
	user: str
	database: str
	port: int = 5432

	def construct_sqlalchemy_url(self, driver: str = "asyncpg") -> str:
		return URL.create(
			drivername=f"postgresql+{driver}",
			username=self.user,
			password=self.password,
			host=self.host,
			port=self.port,
			database=self.database,
		).render_as_string(hide_password=False)

	@classmethod
	def from_env(cls, env: Env) -> "DbConfig":
		return cls(
			host=env.str("DB_HOST"),
			password=env.str("POSTGRES_PASSWORD"),
			user=env.str("POSTGRES_USER"),
			database=env.str("POSTGRES_DB"),
			port=env.int("DB_PORT", 5432),
		)


@dataclass(frozen=True)
class RedisConfig:
	host: str
	port: int
	password: str
	database: int = 0

	def dsn(self) -> str:
		credentials = f":{self.password}@" if self.password else ""
		return f"redis://{credentials}{self.host}:{self.port}/{self.database}"

	@classmethod
	def from_env(cls, env: Env) -> "RedisConfig":
		return cls(
			host=env.str("REDIS_HOST"),
			port=env.int("REDIS_PORT"),
			password=env.str("REDIS_PASSWORD", ""),
			database=env.int("REDIS_DB", 0),
		)


@dataclass(frozen=True)
class Config:
	db: DbConfig
	redis: RedisConfig


def load_config(path: str | None = None) -> Config:
	env = Env()
	env.read_env(path)
	return Config(db=DbConfig.from_env(env), redis=RedisConfig.from_env(env))

config = load_config()


async def get_redis():
	redis = await get_redis_from_url(config.redis.dsn())
	try:
		yield redis
	finally:
		await redis.close()
