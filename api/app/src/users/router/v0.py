from typing import Annotated, Any

import casbin
from fastapi import Body, Depends, HTTPException
from fastapi import status as http_status
from fastapi_pagination.api import create_page, resolve_params
from fastapi_pagination.default import Page, Params
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http.api_router import APIRouter
from app.core.settings import settings
from app.errors import api_disabled
from app.schemas import create_successful_response, SuccessfulResponse
from app.src.authen.dependencies import (
    get_current_active_authorized,
)
from app.src.dependencies import get_async_cache, get_casbin_enforcer, get_db
from app.utils import get_limit_offset, get_params

from .. import db_models, schemas
from ..errors import exists_email, user_not_found
from ..services import user_service

router = APIRouter()

Db = Annotated[AsyncSession, Depends(get_db)]
CacheConnection = Annotated[Redis, Depends(get_async_cache)]
CurrentUser = Annotated[db_models.User, Depends(get_current_active_authorized)]
CasbinEnforcer = Annotated[casbin.AsyncEnforcer, Depends(get_casbin_enforcer)]


@router.get("/", response_model=SuccessfulResponse[Page[schemas.User]])
async def read_users(
    *,
    db: Db,
    params: Annotated[Params, Depends(get_params)],
    current_user: CurrentUser,
) -> Any:
    """
    Retrieve users.
    """
    params = resolve_params(params)
    limit, offset = get_limit_offset(params)

    users, total = await user_service.get_multi_count(db, offset=offset, limit=limit)
    return create_successful_response(data=create_page(users, total, params))


@router.post("/", response_model=SuccessfulResponse[schemas.User])
async def create_user(
    *,
    db: Db,
    casbin_enforcer: CasbinEnforcer,
    user_in: schemas.UserCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create new user.
    """
    return create_successful_response(
        data=await user_service.create_user(db=db, enforcer=casbin_enforcer, obj_in=user_in)
    )


@router.patch("/me", response_model=SuccessfulResponse[schemas.User])
async def update_user_me(
    *,
    db: Db,
    cache_connection: CacheConnection,
    user_in: schemas.UserUpdateMe,
    current_user: CurrentUser,
) -> Any:
    """
    Update own user.
    """
    user = await user_service.get(db, id=current_user.id)
    if not user:
        raise user_not_found()

    if user_in.password is not None:
        await user_service.update_password(
            db=db,
            cache_connection=cache_connection,
            db_obj=user,
            new_password=user_in.password,
        )

    return create_successful_response(
        data=await user_service.update_user_me(
            db=db,
            cache_connection=cache_connection,
            db_obj=user,
            full_name=user_in.full_name,
            avatar_url=user_in.avatar_url,
            default_currency=user_in.default_currency,
            language_preference=user_in.language_preference,
        )
    )


@router.get("/me", response_model=SuccessfulResponse[schemas.User])
async def read_user_me(
    *,
    current_user: CurrentUser,
) -> Any:
    """
    Get current user.
    """
    return create_successful_response(data=current_user)


@router.post("/open", response_model=SuccessfulResponse[schemas.User])
async def create_user_open(
    *,
    db: Db,
    casbin_enforcer: CasbinEnforcer,
    user_in: schemas.UserCreateOpen,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USER.OPEN_REGISTRATION:
        raise api_disabled("open user registration not enable")
    user = await user_service.get_by_email(db, cache_connection=None, email=user_in.email)
    if user:
        raise exists_email("email already exists")
    user_in_create = schemas.UserCreate(**user_in.model_dump())
    user = await user_service.create_user(db, enforcer=casbin_enforcer, obj_in=user_in_create)
    return create_successful_response(data=user)


@router.post("/login-update", response_model=SuccessfulResponse[schemas.User])
async def update_last_login(
    *,
    db: Db,
    cache_connection: CacheConnection,
    current_user: CurrentUser,
) -> Any:
    """
    Update last login date for the current user.
    """
    user = await user_service.update_last_login(
        db=db, cache_connection=cache_connection, db_obj=current_user
    )
    return create_successful_response(data=user)


@router.post("/two-factor/enable", response_model=SuccessfulResponse[schemas.User])
async def enable_two_factor(
    *,
    db: Db,
    cache_connection: CacheConnection,
    secret: Annotated[str, Body()],
    current_user: CurrentUser,
) -> Any:
    """
    Enable two-factor authentication for the current user.
    """
    user = await user_service.enable_two_factor(
        db=db, cache_connection=cache_connection, db_obj=current_user, secret=secret
    )
    return create_successful_response(data=user)


@router.post("/two-factor/disable", response_model=SuccessfulResponse[schemas.User])
async def disable_two_factor(
    *,
    db: Db,
    cache_connection: CacheConnection,
    current_user: CurrentUser,
) -> Any:
    """
    Disable two-factor authentication for the current user.
    """
    user = await user_service.disable_two_factor(
        db=db, cache_connection=cache_connection, db_obj=current_user
    )
    return create_successful_response(data=user)


@router.get("/{user_id}", response_model=SuccessfulResponse[schemas.User])
async def read_user_by_id(
    *,
    user_id: int,
    current_user: CurrentUser,
    db: Db,
) -> Any:
    """
    Get a specific user by id.
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise user_not_found()
    if user == current_user:
        return create_successful_response(data=user)
    return create_successful_response(data=user)


@router.put("/{user_id}", response_model=SuccessfulResponse[schemas.User])
async def update_user(
    *,
    db: Db,
    cache_connection: CacheConnection,
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update a user.
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise user_not_found()
    updated_user = await user_service.update(
        db, cache_connection=cache_connection, db_obj=user, obj_in=user_in
    )
    return create_successful_response(data=updated_user)


@router.put("/{user_id}/status", response_model=SuccessfulResponse[schemas.User])
async def update_user_status(
    *,
    db: Db,
    cache_connection: CacheConnection,
    user_id: int,
    status: Annotated[str, Body()],
    current_user: CurrentUser,
) -> Any:
    """
    Update a user's account status (ACTIVE, SUSPENDED, DELETED).
    """
    if status not in ["ACTIVE", "SUSPENDED", "DELETED"]:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be one of: ACTIVE, SUSPENDED, DELETED",
        )

    user = await user_service.get(db, id=user_id)
    if not user:
        raise user_not_found()

    user = await user_service.update_account_status(
        db=db, cache_connection=cache_connection, db_obj=user, status=status
    )
    return create_successful_response(data=user)
