from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator, Awaitable, Callable, ParamSpec, TypeVar

from loguru import logger
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.settings import settings

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class AsyncDbConnection:
    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_maker: async_sessionmaker[AsyncSession] | None = None

    def init(self) -> None:
        # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#prepared-statement-name-with-pgbouncer
        self.engine = create_async_engine(
            settings.POSTGRES.ASYNC_DATABASE_URI,
            echo=settings.SQLALCHEMY.ECHO,
            pool_pre_ping=True,
            future=True,
            poolclass=NullPool,
            # connect_args={
            #     "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
            # },
            isolation_level="REPEATABLE READ",
        )
        self.session_maker = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def close(self) -> None:
        if self.engine is None:
            logger.warning("can't close connection not init")
            return

        await self.engine.dispose()
        self.engine = None
        self.session_marker = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        assert self.session_maker is not None, "must call async_db_connection.init() before"

        async with self.session_maker() as session:
            yield session

    def inject(
        self,
        func: Callable[Param, Awaitable[RetType]],
    ) -> Callable[..., Awaitable[RetType]]:
        @wraps(func)
        async def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            async with self.session() as db:
                kwargs["db"] = db
                return await func(*args, **kwargs)

        return wrapper


async_db_connection = AsyncDbConnection()
