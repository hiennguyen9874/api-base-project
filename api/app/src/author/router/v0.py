from typing import Annotated, Any

import casbin
from fastapi import Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http.api_router import APIRouter
from app.src.authen.dependencies import get_current_active_authorized
from app.src.dependencies import get_casbin_enforcer, get_db
from app.src.users.db_models import User

from .. import schemas
from ..services import casbin_service

router = APIRouter()


Db = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_authorized)]
CasbinEnforcer = Annotated[casbin.AsyncEnforcer, Depends(get_casbin_enforcer)]


@router.get("/policy")
async def get_all_policies(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
) -> Any:
    return await casbin_service.get_policy_list(enforcer=casbin_enforcer)


@router.get("/policy/{role}/all")
async def get_role_policies(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    role: str,
) -> Any:
    return await casbin_service.get_policy_list_by_role(enforcer=casbin_enforcer, role=role)


@router.post("/policy")
async def create_policy(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    p: schemas.Policy,
) -> Any:
    return await casbin_service.create_policy(enforcer=casbin_enforcer, p=p)


@router.post("/policies")
async def create_policies(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    ps: list[schemas.Policy],
) -> Any:
    return await casbin_service.create_policies(enforcer=casbin_enforcer, ps=ps)


@router.put("/policy")
async def update_policy(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    old: schemas.Policy,
    new: schemas.Policy,
) -> Any:
    return await casbin_service.update_policy(enforcer=casbin_enforcer, old=old, new=new)


@router.put("/policies")
async def update_policies(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    old: list[schemas.Policy],
    new: list[schemas.Policy],
) -> Any:
    return await casbin_service.update_policies(enforcer=casbin_enforcer, old=old, new=new)


@router.delete("/policy")
async def delete_policy(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    p: schemas.Policy,
) -> Any:
    return await casbin_service.delete_policy(enforcer=casbin_enforcer, p=p)


@router.delete("/policies")
async def delete_policies(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    ps: list[schemas.Policy],
) -> Any:
    return await casbin_service.delete_policies(enforcer=casbin_enforcer, ps=ps)


@router.get("/group")
async def get_all_groups(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
) -> Any:
    return await casbin_service.get_group_list(enforcer=casbin_enforcer)


@router.post("/group")
async def create_group(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    g: schemas.Group,
) -> Any:
    return await casbin_service.create_group(enforcer=casbin_enforcer, g=g)


@router.post("/groups")
async def create_groups(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    gs: list[schemas.Group],
) -> Any:
    return await casbin_service.create_groups(enforcer=casbin_enforcer, gs=gs)


@router.delete("/group")
async def delete_group(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    g: schemas.Group,
) -> Any:
    return await casbin_service.delete_group(enforcer=casbin_enforcer, g=g)


@router.delete("/groups")
async def delete_groups(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    gs: list[schemas.Group],
) -> Any:
    return await casbin_service.delete_groups(enforcer=casbin_enforcer, gs=gs)


@router.post("/has-group")
async def has_grouping(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    g: schemas.Group,
) -> Any:
    return await casbin_service.has_grouping(enforcer=casbin_enforcer, g=g)


@router.get("/roles/")
async def get_all_roles(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
) -> Any:
    return await casbin_service.get_all_roles(enforcer=casbin_enforcer)


@router.get("/roles/get-users/{role}")
async def get_users_for_role(
    *,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    role: str,
) -> Any:
    return await casbin_service.get_users_for_role(enforcer=casbin_enforcer, role=role)


@router.get("/roles/{user_email}")
async def get_roles_for_user(
    *,
    db: Db,
    # current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    user_email: str,
) -> Any:
    return await casbin_service.get_roles_for_user(
        db=db, enforcer=casbin_enforcer, email=user_email
    )


@router.post("/roles/")
async def add_role_for_user(
    *,
    db: Db,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    email: Annotated[str, Body()],
    role: Annotated[str, Body()],
) -> Any:
    return await casbin_service.add_role_for_user(
        db=db,
        enforcer=casbin_enforcer,
        email=email,
        role=role,
        available_roles=list(
            await casbin_service.get_roles_for_user(
                db=db, enforcer=casbin_enforcer, email=current_user.email
            )
        ),
    )


@router.delete("/roles/")
async def delete_role_for_user(
    *,
    db: Db,
    current_user: CurrentUser,
    casbin_enforcer: CasbinEnforcer,
    email: Annotated[str, Body()],
    role: Annotated[str, Body()],
) -> Any:
    return await casbin_service.delete_role_for_user(
        db=db, enforcer=casbin_enforcer, email=email, role=role
    )
