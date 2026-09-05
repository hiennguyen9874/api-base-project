from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis


class RefreshTokenRepository:
    @staticmethod
    def _key(email: str) -> str:
        return f"RefreshToken:{email}"

    async def check(self, connection: Redis, email: str, token: str) -> bool:
        key = self._key(email)
        async with connection.pipeline(transaction=True) as pipe:
            results = await (
                pipe.zremrangebyscore(
                    key,
                    "-inf",
                    (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp(),
                )
                .zscore(key, token)
                .execute()
            )
        return results[-1] is not None

    async def delete(self, connection: Redis, email: str, token: str) -> None:
        key = self._key(email)
        async with connection.pipeline(transaction=True) as pipe:
            await (
                pipe.zrem(key, token)
                .zremrangebyscore(
                    key,
                    "-inf",
                    (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp(),
                )
                .execute()
            )

    async def add(
        self,
        connection: Redis,
        email: str,
        token: str,
        expire: datetime,
    ) -> None:
        key = self._key(email)
        async with connection.pipeline(transaction=True) as pipe:
            await (
                pipe.zadd(key, {token: expire.timestamp()}, gt=True)
                .expireat(key, when=expire)
                .zremrangebyscore(
                    key,
                    "-inf",
                    (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp(),
                )
                .execute()
            )

    async def delete_all(self, connection: Redis, email: str) -> None:
        await connection.delete(self._key(email))


refresh_token_repository = RefreshTokenRepository()
