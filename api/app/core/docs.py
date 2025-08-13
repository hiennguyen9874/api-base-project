from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from app import errors
from app.core.settings import settings


def configure_swagger(app: FastAPI) -> None:
    """Configure Swagger UI and documentation."""

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> Any:
        if not settings.APP.ENABLE_DOCS:
            raise errors.not_found("docs not enable, please set ENABLE_DOCS=true")

        return get_swagger_ui_html(
            openapi_url=app.openapi_url,  # type: ignore
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            swagger_favicon_url="/static/favicon.png",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
    async def swagger_ui_redirect() -> Any:
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> Any:
        if not settings.APP.ENABLE_DOCS:
            raise errors.not_found("docs not enable, please set ENABLE_DOCS=true")

        return get_redoc_html(
            openapi_url=app.openapi_url,  # type: ignore
            title=app.title + " - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
            redoc_favicon_url="/static/favicon.png",
        )
