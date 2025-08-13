from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, AsyncGenerator, Callable, Mapping

from fastapi import FastAPI
from loguru import logger
from taskiq_aio_pika import AioPikaBroker

from app.core.connections import connections
from app.src.author.casbin_enforcer import init_casbin_enforcer


async def init_connections() -> None:
    """Initialize all connections required by the application."""
    await connections.init_all()


async def close_connections() -> None:
    """Close all connections."""
    await connections.close_all()


async def init_services() -> dict[str, Any]:
    """Initialize application services."""
    # Initialize the Casbin enforcer
    casbin_enforcer = await init_casbin_enforcer()

    return {"casbin_enforcer": casbin_enforcer}


async def finalize_services(services: dict[str, Any]) -> None:
    """Finalize services before shutdown."""
    if "casbin_enforcer" in services:
        casbin_enforcer = services["casbin_enforcer"]

        # Save casbin policy with locking
        async with connections.lock.lock(
            name="api-casbin-save-policy",
            lock_timeout=5 * 60,
            acquire_timeout=5 * 60,
            acquire_failed_msg="Cannot acquire redis startup lock",
            raise_error=True,
        ):
            await casbin_enforcer.save_policy()  # type: ignore[attr-defined]


def get_lifespan(
    broker: AioPikaBroker,
) -> (
    Callable[[FastAPI], AsyncContextManager[None]]
    | Callable[[FastAPI], AsyncContextManager[Mapping[str, Any]]]
    | None
):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[dict[str, Any], None]:  # type: ignore[type-arg]
        """FastAPI lifespan context manager for startup and shutdown events."""
        logger.info("FastAPI startup...")

        # Initialize connections
        await init_connections()

        # Initialize services
        services = await init_services()

        if not broker.is_worker_process:
            await broker.startup()

        yield services

        if not broker.is_worker_process:
            await broker.shutdown()

        # Finalize services
        await finalize_services(services)

        # Close connections
        await close_connections()

        logger.info("FastAPI shutdown...")

    return lifespan
