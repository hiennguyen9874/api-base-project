from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator, Awaitable, Callable, ParamSpec, TypeVar

from loguru import logger
from redis.asyncio import ConnectionPool, Redis

from app.core.settings import settings

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class AsyncCacheConnection:
    def __init__(self) -> None:
        self.pool: ConnectionPool | None = None

    def init(self, max_connections: int) -> None:
        if not settings.REDIS_CACHE.URL:
            raise RuntimeError("REDIS_CACHE.URL must be not None")

        self.pool = ConnectionPool.from_url(
            url=str(settings.REDIS_CACHE.URL),
            decode_responses=False,
            max_connections=max_connections,
        )

    async def close(self) -> None:
        if self.pool is None:
            logger.warning("can't close connection not init")
            return

        await self.pool.disconnect()
        self.pool = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[Redis, None]:
        assert self.pool is not None, "must call async_cache_connection.init() before"
        async with Redis(connection_pool=self.pool) as redis:
            yield redis

    def inject(
        self,
        func: Callable[Param, Awaitable[RetType]],
    ) -> Callable[..., Awaitable[RetType]]:
        @wraps(func)
        async def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            async with self.session() as cache_connection:
                kwargs["cache_connection"] = cache_connection
                return await func(*args, **kwargs)

        return wrapper


async_cache_connection = AsyncCacheConnection()
