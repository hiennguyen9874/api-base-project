import asyncio

from loguru import logger

from app.core.connections import connections
from app.core.initialization import close_connections, init_connections
from app.core.logging.custom_logging import make_customize_logger
from app.core.settings import settings
from app.src.users.init_superuser import init_superuser

make_customize_logger(settings.APP.CONFIG_DIR / "logging" / "prestart.json")


async def init() -> None:
    await init_connections()

    async with connections.db.session() as db:
        await init_superuser(db=db)
        await db.commit()

    await close_connections()


def main() -> None:
    logger.info("Creating initial data")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.close()

    logger.info("Initial data created")


if __name__ == "__main__":
    main()
