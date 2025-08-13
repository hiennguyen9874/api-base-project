from typing import Annotated, Any

from fastapi import Depends
from fastapi_pagination.api import create_page, resolve_params
from fastapi_pagination.default import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http.api_router import APIRouter
from app.schemas import create_successful_response, SuccessfulResponse
from app.src.authen.dependencies import get_current_active_authorized
from app.src.dependencies import get_db
from app.src.users.db_models import User
from app.utils import get_limit_offset, get_params

from .. import errors, schemas
from ..services import item_service

router = APIRouter()

CurrentUser = Annotated[User, Depends(get_current_active_authorized)]
Db = Annotated[AsyncSession, Depends(get_db)]


@router.post("/", response_model=SuccessfulResponse[schemas.Item])
async def create_item(
    *,
    db: Db,
    item_in: schemas.ItemCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create new item.
    """
    item = await item_service.create_with_owner(db=db, obj_in=item_in, owner_id=current_user.id)
    return create_successful_response(data=item)


@router.get("/", response_model=SuccessfulResponse[Page[schemas.Item]])
async def read_items(
    *,
    db: Db,
    params: Annotated[Params, Depends(get_params)],
    current_user: CurrentUser,
) -> Any:
    """
    Retrieve items.
    """
    params = resolve_params(params)  # type: ignore
    limit, offset = get_limit_offset(params)

    items, total = await item_service.get_multi_count(db, offset=offset, limit=limit)
    return create_successful_response(data=create_page(items, total, params))


@router.get("/{id}", response_model=SuccessfulResponse[schemas.Item])
async def read_item(
    *,
    db: Db,
    id: int,
    current_user: CurrentUser,
) -> Any:
    """
    Get item by ID.
    """
    item = await item_service.get(db=db, id=id)
    if not item:
        raise errors.item_not_found()
    return create_successful_response(data=item)


@router.put("/{id}", response_model=SuccessfulResponse[schemas.Item])
async def update_item(
    *,
    db: Db,
    id: int,
    item_in: schemas.ItemUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update an item.
    """
    item = await item_service.get(db=db, id=id)
    if not item:
        raise errors.item_not_found()
    item = await item_service.update(db=db, db_obj=item, obj_in=item_in)
    return create_successful_response(data=item)


@router.delete("/{id}", response_model=SuccessfulResponse[schemas.Item])
async def delete_item(
    *,
    db: Db,
    id: int,
    current_user: CurrentUser,
) -> Any:
    """
    Delete an item.
    """
    item = await item_service.get(db=db, id=id)

    if not item:
        raise errors.item_not_found()

    await item_service.delete_by_id(db=db, id=id)

    return create_successful_response(data=item)
