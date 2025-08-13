from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Coroutine, ParamSpec, TypeVar

from loguru import logger
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.lock import Lock as RedisLock

from app.core.settings import settings

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


DEFAULT_ACQUIRE_FAILED_MSG = "can not acquire redis lock"


class AsyncLock:
    def __init__(self) -> None:
        self.pool: ConnectionPool | None = None

    def init(self, max_connections: int) -> None:
        self.pool = ConnectionPool(
            host=settings.REDIS_LOCK.HOST,
            port=settings.REDIS_LOCK.PORT,
            db=settings.REDIS_LOCK.DB,
            max_connections=max_connections,
            decode_responses=True,
        )

    async def close(self) -> None:
        if self.pool is None:
            logger.warning("can't close connection not init")
            return
        await self.pool.disconnect()
        self.pool = None

    @asynccontextmanager
    async def lock(
        self,
        name: str,
        lock_timeout: int,
        acquire_timeout: int,
        acquire_failed_msg: str,
        raise_error: bool = False,
    ) -> AsyncGenerator[None, None]:
        assert self.pool is not None, "must call async_lock.init() before"
        redis = Redis(connection_pool=self.pool)

        redis_lock = RedisLock(redis, name, timeout=lock_timeout, blocking_timeout=acquire_timeout)

        acquired = await redis_lock.acquire()
        if not acquired:
            if raise_error:
                raise RuntimeError(acquire_failed_msg)
            else:
                # Short-circuit: Don't yield, don't raise — return a no-op context
                return  # This is okay — we're not in a `with` yet

        try:
            yield
        finally:
            await redis_lock.release()

    def inject(
        self,
        name: str,
        lock_timeout: int = 5 * 60,
        acquire_timeout: int = 2 * 60,
        acquire_failed_msg: str = DEFAULT_ACQUIRE_FAILED_MSG,
        raise_error: bool = False,
    ) -> Callable[
        [Callable[Param, RetType | None]],
        Callable[Param, Coroutine[Any, Any, RetType | None]],
    ]:
        def decorator(
            func: Callable[Param, RetType | None],
        ) -> Callable[Param, Coroutine[Any, Any, RetType | None]]:
            @wraps(func)
            async def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType | None:
                async with self.lock(
                    name=name,
                    lock_timeout=lock_timeout,
                    acquire_timeout=acquire_timeout,
                    acquire_failed_msg=acquire_failed_msg,
                    raise_error=raise_error,
                ):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    async def release_all_locks(self) -> None:
        if self.pool is None:
            logger.warning("can't close connection not init")
            return
        redis = Redis(connection_pool=self.pool)
        await redis.flushall()


async_lock = AsyncLock()
