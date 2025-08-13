from typing import Annotated

import casbin
from fastapi import Cookie, Depends, Header
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app import errors as app_errors
from app.core.auth.security import decode_token
from app.core.settings import settings
from app.src.dependencies import get_async_cache, get_casbin_enforcer, get_db
from app.src.users.db_models import User

from . import errors
from .services import authen_service


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        if access_token := request.cookies.get("access_token"):
            return access_token
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        return None if not authorization or scheme.lower() != "bearer" else param


reusable_oauth2 = OAuth2PasswordBearerWithCookie(
    token_url=f"{settings.APP.API_PREFIX}/v0/authen/login"
)


def is_local_token(token: str) -> bool:
    try:
        decode_token(token, settings.TOKEN.ACCESS_TOKEN_SECRET_KEY)
        return True
    except InvalidTokenError:
        return False


async def get_current_user_from_oauth2(
    *,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    async_cache: Annotated[Redis, Depends(get_async_cache)],
    token_oauth2: Annotated[str, Depends(reusable_oauth2)],
) -> User:
    user = await authen_service.get_user_from_token(
        db, cache_connection=async_cache, token=token_oauth2
    )
    if not user:
        raise app_errors.not_found("not found user")

    return user


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    async_cache: Annotated[Redis, Depends(get_async_cache)],
    token_oauth2: Annotated[str | None, Depends(reusable_oauth2)],
) -> User:
    if token_oauth2 is not None:
        return await get_current_user_from_oauth2(
            request=request,
            db=db,
            async_cache=async_cache,
            token_oauth2=token_oauth2,
        )

    raise errors.not_authenticated("Not authenticated (oauth2)")


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise errors.inactive_user("inactive user")
    return current_user


async def get_current_active_authorized(
    *,
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    casbin_enforcer: Annotated[casbin.AsyncEnforcer, Depends(get_casbin_enforcer)],
) -> User:
    method = request.method
    path = request.url.path.replace(f"{settings.APP.API_PREFIX}", "")

    if not path.endswith("/"):
        path = f"{path}/"

    await casbin_enforcer.load_policy()
    if not casbin_enforcer.enforce(current_user.email, path, method):
        raise app_errors.forbidden("user doesn't have enough privileges")

    return current_user


async def get_current_media_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    async_cache: Annotated[Redis, Depends(get_async_cache)],
    token_oauth2: Annotated[str | None, Depends(reusable_oauth2)],
) -> User | None:
    if not settings.APP.PROTECT_MEDIA:
        return None

    if token_oauth2 is not None:
        return await get_current_user_from_oauth2(
            request=request,
            db=db,
            async_cache=async_cache,
            token_oauth2=token_oauth2,
        )

    raise errors.not_authenticated("Not authenticated (oidc, oauth2)")


async def get_refresh_token(
    cookie_refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
    header_refresh_token: Annotated[str | None, Header(alias="refresh_token")] = None,
) -> str | None:
    if cookie_refresh_token is not None:
        return cookie_refresh_token
    if header_refresh_token is not None:
        return header_refresh_token
    raise errors.refresh_token_not_found("refresh_token not set in cookie or header")
