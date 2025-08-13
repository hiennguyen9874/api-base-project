from typing import Any, ParamSpec, TypeVar

from redis.asyncio import Redis

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class BaseCacheRepository:
    def __init__(self, repository_name: str) -> None:
        pass

    async def create(self, connection: Redis, key: str, value: Any, ttl: int | None = None) -> None:
        await connection.set(key, value, ex=ttl)

    async def get(self, connection: Redis, key: str, ttl: int | None = None) -> Any | None:
        value = await connection.get(key)
        if value is None:
            return None
        if ttl is not None:
            await connection.expire(name=key, time=ttl, gt=True)
        return value

    async def delete(self, connection: Redis, key: str) -> None:
        await connection.delete(key)

    async def set_add(self, connection: Redis, key: str, value: str) -> None:
        await connection.sadd(key, value)

    async def set_adds(self, connection: Redis, key: str, values: list[str]) -> None:
        await connection.sadd(key, *values)

    async def set_is_member(self, connection: Redis, key: str, value: str) -> bool:
        return await connection.sismember(key, value)

    async def set_delete(self, connection: Redis, key: str, value: str) -> None:
        await connection.srem(key, value)
