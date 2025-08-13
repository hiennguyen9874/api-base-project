from typing import AsyncGenerator, AsyncIterator

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.cache.cache_connections import async_cache_connection
from app.core.db.db_connections import async_db_connection
from app.errors import internal_server_error


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_db_connection.session() as session:
        yield session


async def get_async_cache() -> AsyncIterator[redis.Redis]:
    async with async_cache_connection.session() as es:
        yield es


async def get_casbin_enforcer(request: Request) -> AsyncGenerator:
    if not hasattr(request.state, "casbin_enforcer"):
        raise internal_server_error("can not connect to casbin enforcer")
    return request.state.casbin_enforcer
