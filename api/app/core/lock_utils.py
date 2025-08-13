from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.cache import async_lock


@asynccontextmanager
async def with_lock(name: str, timeout: int = 300) -> AsyncGenerator[None, None]:
    """
    Context manager for easily acquiring and releasing a distributed lock.

    Args:
        name: Unique name for the lock
        timeout: Lock and acquire timeout in seconds

    Yields:
        None: When the lock is successfully acquired

    Raises:
        RuntimeError: If the lock cannot be acquired
    """
    async with async_lock.lock(
        name=name,
        lock_timeout=timeout,
        acquire_timeout=timeout,
        acquire_failed_msg=f"Cannot acquire {name} lock",
        raise_error=True,
    ):
        yield
