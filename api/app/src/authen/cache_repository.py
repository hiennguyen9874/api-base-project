from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis

from app.src.cache_repository import BaseCacheRepository


class AuthenCacheRepository(BaseCacheRepository):
    ## Common
    @staticmethod
    def _generate_redis_refresh_token_by_email(
        email: str,
    ) -> str:  # pylint: disable=redefined-builtin
        return f"RefreshToken:{email}"

    async def check_refresh_token(
        self, connection: Redis, obj_email: str, refresh_token: str
    ) -> bool:
        async with connection.pipeline(transaction=True) as pipe:
            results = await (
                pipe.zremrangebyscore(
                    self._generate_redis_refresh_token_by_email(obj_email),
                    "-inf",
                    (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp(),
                )
                .zscore(
                    connection,
                    self._generate_redis_refresh_token_by_email(obj_email),
                    refresh_token,
                )
                .execute()
            )

        return results[-1] is not None

    async def delete_refresh_token(
        self, connection: Redis, obj_email: str, refresh_token: str
    ) -> None:
        async with connection.pipeline(transaction=True) as pipe:
            await (
                pipe.zrem(
                    self._generate_redis_refresh_token_by_email(obj_email),
                    refresh_token,
                )
                .zremrangebyscore(
                    self._generate_redis_refresh_token_by_email(obj_email),
                    "-inf",
                    (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp(),
                )
                .execute()
            )

    async def add_refresh_token(
        self, connection: Redis, obj_email: str, refresh_token: str, expire: datetime
    ) -> None:
        async with connection.pipeline(transaction=True) as pipe:
            await (
                pipe.zadd(
                    self._generate_redis_refresh_token_by_email(obj_email),
                    {refresh_token: expire.timestamp()},
                    gt=True,
                )
                .expireat(
                    self._generate_redis_refresh_token_by_email(obj_email),
                    when=expire,
                )
                .zremrangebyscore(
                    self._generate_redis_refresh_token_by_email(obj_email),
                    "-inf",
                    (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp(),
                )
                .execute()
            )

    async def delete_all_refresh_token(self, connection: Redis, obj_email: str) -> None:
        await self.delete(
            connection,
            self._generate_redis_refresh_token_by_email(obj_email),
        )


authen_cache_repository = AuthenCacheRepository(repository_name="authen")
