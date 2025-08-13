from loguru import logger

from app.core.cache import async_cache_connection, async_lock
from app.core.db.db_connections import async_db_connection
from app.core.settings import settings


class ConnectionManager:
    """
    Unified connection manager for handling all application connections.
    This class simplifies connection initialization and cleanup.
    """

    def __init__(self) -> None:
        self.db = async_db_connection
        self.cache = async_cache_connection
        self.lock = async_lock

    async def init_all(self) -> None:
        """Initialize all connections required by the application."""
        logger.info("Initializing all connections")

        # Initialize database connections
        self.db.init()

        # Initialize cache connections
        self.cache.init(max_connections=settings.REDIS_CACHE.API_MAX_CONNECTIONS)

        # Initialize lock connections
        self.lock.init(max_connections=settings.REDIS_LOCK.API_MAX_CONNECTIONS)

        logger.info("All connections initialized successfully")

    async def close_all(self) -> None:
        """Close all connections."""
        logger.info("Closing all connections")

        # Close database connections
        await self.db.close()

        # Close cache connections
        await self.cache.close()

        # Close lock connections
        await self.lock.close()

        logger.info("All connections closed successfully")


# Singleton instance
connections = ConnectionManager()
