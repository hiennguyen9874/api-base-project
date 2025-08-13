import asyncio

from loguru import logger

from app.core.connections import connections
from app.core.initialization import (
    close_connections,
    finalize_services,
    init_connections,
    init_services,
)
from app.core.logging.custom_logging import make_customize_logger
from app.core.settings import settings
from app.src.author.init_casbin import init_casbin
from app.src.users.init_superuser import init_superuser

make_customize_logger(settings.APP.CONFIG_DIR / "logging" / "prestart.json")


async def init() -> None:
    # Initialize connections
    await init_connections()

    # Initialize services (includes casbin enforcer)
    services = await init_services()
    casbin_enforcer = services["casbin_enforcer"]

    # Initialize superuser
    async with connections.db.session() as db:
        await init_superuser(
            db=db,
            enforcer=casbin_enforcer,
        )
        await db.commit()

    # Initialize casbin policies
    await init_casbin(casbin_enforcer)

    # Finalize services (saves casbin policy)
    await finalize_services(services)

    # Close connections
    await close_connections()


def main() -> None:
    logger.info("Creating initial data")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.close()

    logger.info("Initial data created")


if __name__ == "__main__":
    main()
