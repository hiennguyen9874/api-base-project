from typing import AsyncIterator

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache.cache_connections import async_cache_connection
from app.core.db.db_connections import async_db_connection


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_db_connection.session() as session:
        yield session


async def get_async_cache() -> AsyncIterator[redis.Redis]:
    async with async_cache_connection.session() as es:
        yield es
