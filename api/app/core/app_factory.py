import taskiq_fastapi
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.docs import configure_swagger
from app.core.http.exception_handlers import register_exception_handlers
from app.core.http.middleware import setup_middleware
from app.core.initialization import get_lifespan
from app.core.messaging.taskiq_broker import broker as taskiq_broker_app
from app.core.ratelimit import limiter
from app.core.settings import settings
from app.src.route import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP.NAME,
        version=settings.APP.VERSION,
        openapi_url="/openapi.json",
        swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
        docs_url=None,
        redoc_url=None,
        debug=False,
        default_response_class=ORJSONResponse,
        lifespan=get_lifespan(taskiq_broker_app),
    )

    taskiq_fastapi.init(taskiq_broker_app, app)

    # Configure swagger UI settings
    app.swagger_ui_init_oauth = {
        "usePkceWithAuthorizationCodeGrant": True,
        "useBasicAuthenticationWithAccessCodeGrant": True,
        "appName": "fastapi-keycloak-demo",
    }

    # Configure swagger documentation
    configure_swagger(app)

    # Configure rate limiter
    app.state.limiter = limiter

    # Mount static files
    app.mount("/static", StaticFiles(directory=settings.APP.STATIC_DIR), name="static")

    # Register routes
    app.include_router(api_router, prefix=f"{settings.APP.API_PREFIX}")

    # Register exception handlers
    register_exception_handlers(app)

    # Configure middleware
    setup_middleware(app)

    return app
