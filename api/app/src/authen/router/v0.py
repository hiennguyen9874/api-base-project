from typing import Annotated, Any

from fastapi import Body, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http.api_router import APIRouter
from app.core.ratelimit import limiter
from app.core.settings import settings
from app.schemas import (
    create_successful_response,
    ErrorResponse,
    Msg,
)
from app.src.dependencies import get_async_cache, get_db
from app.src.users.db_models import User

from .. import schemas
from ..dependencies import (
    get_current_media_user,
    get_refresh_token,
)
from ..services import authen_service

router = APIRouter()

Db = Annotated[AsyncSession, Depends(get_db)]
CacheConnection = Annotated[Redis, Depends(get_async_cache)]


@router.post(
    "/login",
    response_model=schemas.Token,
    responses={
        403: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Inactive user or The user doesn't have enough privileges",
        },
    },
)
@limiter.limit(settings.RATELIMIT.LOGIN_RATELIMIT1)
@limiter.limit(settings.RATELIMIT.LOGIN_RATELIMIT2)
async def login_access_token(
    request: Request,
    response: Response,
    *,
    db: Db,
    cache_connection: CacheConnection,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    (
        access_token,
        refresh_token,
        access_token_expire,
        refresh_token_expire,
    ) = await authen_service.login(
        db=db,
        cache_connection=cache_connection,
        email=form_data.username,
        password=form_data.password,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=settings.TOKEN.COOKIE_HTTPONLY,
        secure=settings.TOKEN.COOKIE_SECURE,
        samesite=settings.TOKEN.COOKIE_SAMESITE,
        expires=access_token_expire,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.TOKEN.COOKIE_HTTPONLY,
        secure=settings.TOKEN.COOKIE_SECURE,
        samesite=settings.TOKEN.COOKIE_SAMESITE,
        expires=refresh_token_expire,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token(
    response: Response,
    *,
    db: Db,
    cache_connection: CacheConnection,
    refresh_token: Annotated[str, Depends(get_refresh_token)],
) -> Any:
    (
        access_token,
        refresh_token,
        access_token_expire,
        refresh_token_expire,
    ) = await authen_service.refresh_token(
        db=db,
        cache_connection=cache_connection,
        old_refresh_token=refresh_token,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=settings.TOKEN.COOKIE_HTTPONLY,
        secure=settings.TOKEN.COOKIE_SECURE,
        samesite=settings.TOKEN.COOKIE_SAMESITE,
        expires=access_token_expire,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.TOKEN.COOKIE_HTTPONLY,
        secure=settings.TOKEN.COOKIE_SECURE,
        samesite=settings.TOKEN.COOKIE_SAMESITE,
        expires=refresh_token_expire,
    )

    return create_successful_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    *,
    cache_connection: CacheConnection,
    refresh_token: Annotated[str, Depends(get_refresh_token)],
) -> None:
    await authen_service.logout(cache_connection=cache_connection, refresh_token=refresh_token)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    response: Response,
    *,
    cache_connection: CacheConnection,
    refresh_token: Annotated[str, Depends(get_refresh_token)],
) -> None:
    await authen_service.logout_all_with_token(
        cache_connection=cache_connection, refresh_token=refresh_token
    )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.post(
    "/password-recovery/{email}",
    response_model=Msg,
)
async def recover_password(
    *,
    email: str,
    db: Db,
) -> Any:
    """
    Password Recovery.
    """
    await authen_service.recover_password(db, email=email)

    return {"msg": "Password recovery email sent"}


@router.post(
    "/reset-password",
    response_model=Msg,
)
async def reset_password(
    *,
    token: Annotated[str, Body()],
    new_password: Annotated[str, Body()],
    db: Db,
    cache_connection: CacheConnection,
) -> Any:
    """
    Reset password.
    """
    await authen_service.reset_password(
        db,
        cache_connection=cache_connection,
        token=token,
        new_password=new_password,
    )

    return {"msg": "Password updated successfully"}


@router.get("/auth-static")
async def auth_static(
    current_user: Annotated[User, Depends(get_current_media_user)],
) -> Any:  # NOSONAR
    pass  # method for media authentication
