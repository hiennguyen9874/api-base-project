from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator, Callable

from fastapi import FastAPI
from loguru import logger
from taskiq_aio_pika import AioPikaBroker

from app.core.connections import connections


async def init_connections() -> None:
    """Initialize all connections required by the application."""
    await connections.init_all()


async def close_connections() -> None:
    """Close all connections."""
    await connections.close_all()


def get_lifespan(
    broker: AioPikaBroker,
) -> Callable[[FastAPI], AsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """FastAPI lifespan context manager for startup and shutdown events."""
        logger.info("FastAPI startup...")
        await init_connections()

        if not broker.is_worker_process:
            await broker.startup()

        yield

        if not broker.is_worker_process:
            await broker.shutdown()

        await close_connections()
        logger.info("FastAPI shutdown...")

    return lifespan
