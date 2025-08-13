from redis.asyncio import Redis

from app.core.settings import settings
from app.src.cache_repository import BaseCacheRepository

from .db_models import User
from .schemas import UserInDB


class UserCacheRepository(BaseCacheRepository):
    ## Common
    @staticmethod
    def _generate_redis_user_by_email(
        email: str,
    ) -> str:  # pylint: disable=redefined-builtin
        return f"Cache:User:{email}"

    ## Cache
    async def create_cache_by_email(self, connection: Redis, db_obj: User) -> None:
        user_in_db = UserInDB.model_validate(db_obj)
        await self.create(
            connection=connection,
            key=self._generate_redis_user_by_email(db_obj.email),
            value=user_in_db.model_dump_json(),
            ttl=settings.REDIS_CACHE.USER_TTL,
        )

    async def get_cache_by_email(self, connection: Redis, obj_email: str) -> User | None:
        db_obj = await self.get(
            connection=connection,
            key=self._generate_redis_user_by_email(obj_email),
            ttl=settings.REDIS_CACHE.USER_TTL,
        )
        if not db_obj:
            return None
        user_in_db = UserInDB.model_validate_json(db_obj)
        obj_in_data = user_in_db.model_dump()
        return User(**obj_in_data)

    async def delete_cache_by_email(self, connection: Redis, obj_email: str) -> None:
        await self.delete(connection=connection, key=self._generate_redis_user_by_email(obj_email))


user_cache_repository = UserCacheRepository(repository_name="user")
