import sentry_sdk
from redis.asyncio import ConnectionPool, Redis  # type: ignore
from sentry_sdk.integrations.loguru import LoguruIntegration
from taskiq import TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource

from app.core.initialization import close_connections, init_connections
from app.core.logging.custom_logging import make_customize_logger
from app.core.messaging.taskiq_broker import broker as taskiq_broker_app
from app.core.settings import settings
from app.src.db_models import *  # noqa # NOSONAR
from app.src.db_signals import *  # noqa # NOSONAR
from app.tasks import *  # noqa # NOSONAR

if settings.SENTRY.DSN is not None:
    sentry_sdk.init(
        dsn=str(settings.SENTRY.DSN),
        integrations=[LoguruIntegration()],
        environment=settings.SENTRY.ENVIRONMENT,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        enable_tracing=settings.SENTRY.ENABLE_TRACING,
        traces_sample_rate=settings.SENTRY.TRACES_SAMPLE_RATE,
    )

broker = taskiq_broker_app

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    # Here we store connection pool on startup for later use.

    make_customize_logger(settings.APP.CONFIG_DIR / "logging" / "worker.json")  # type: ignore

    # Initialize all connections using the ConnectionManager
    await init_connections()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    # Here we close our pool on shutdown event.

    # Close all connections using the ConnectionManager
    await close_connections()
