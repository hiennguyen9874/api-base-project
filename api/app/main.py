import sentry_sdk
from fastapi import status
from loguru import logger
from pydantic import BaseModel
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.core.app_factory import create_app
from app.core.logging.custom_logging import make_customize_logger
from app.core.settings import settings
from app.src.db_models import *  # noqa # NOSONAR
from app.src.db_signals import *  # noqa # NOSONAR

make_customize_logger(settings.APP.CONFIG_DIR / "logging" / "api.json")

if settings.SENTRY.DSN is not None:
    logger.info(
        "Init sentry dns: {dsn}, environment: {environment}",
        dsn=settings.SENTRY.DSN,
        environment=settings.SENTRY.ENVIRONMENT,
    )

    sentry_sdk.init(
        dsn=str(settings.SENTRY.DSN),
        environment=settings.SENTRY.ENVIRONMENT,
        integrations=[
            LoguruIntegration(),
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        enable_tracing=settings.SENTRY.ENABLE_TRACING,
        traces_sample_rate=settings.SENTRY.TRACES_SAMPLE_RATE,
    )


# Lifespan function moved to app.core.initialization


# Create_app function moved to app.core.app_factory


# Create the FastAPI application using app_factory
app = create_app()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


# Middleware, exception handlers, static files, and routes are configured in app_factory
