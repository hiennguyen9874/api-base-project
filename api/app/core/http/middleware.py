from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.settings import settings


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application."""
    # Add session middleware
    app.add_middleware(SessionMiddleware, secret_key=settings.APP.SECRET_KEY, https_only=True)

    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.APP.TRUSTED_HOST,
    )

    # Add CORS middleware last
    # https://github.com/tiangolo/fastapi/discussions/7319#discussioncomment-8428957
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(url).strip("/") for url in settings.APP.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
