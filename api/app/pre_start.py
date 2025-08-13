import asyncio

from loguru import logger
from sqlalchemy import text
from tenacity import retry
from tenacity.after import after_log
from tenacity.before import before_log
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from app.core.cache import async_lock
from app.core.connections import connections
from app.core.lock_utils import with_lock
from app.core.logging.custom_logging import make_customize_logger
from app.core.settings import settings

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

make_customize_logger(settings.APP.CONFIG_DIR / "logging" / "prestart.json")


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, "INFO"),  # type: ignore
    after=after_log(logger, "WARNING"),  # type: ignore
)
@logger.catch
async def init() -> None:
    # Initialize all connections
    await connections.init_all()

    # Release all locks
    await async_lock.release_all_locks()

    # Use the with_lock context manager
    async with with_lock(name="pre-start", timeout=5 * 60):
        try:
            # Test database connection
            async with connections.db.session() as db:
                await db.execute(text("SELECT 1"))
                logger.info("Database connection verified")
        except Exception as e:
            logger.error(f"Pre start, error: {str(e)}")
            raise e

    # Close all connections
    await connections.close_all()


def main() -> None:
    logger.info("Pre start, Initializing service")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.close()

    logger.info("Pre start, Service finished initializing")


if __name__ == "__main__":
    main()
