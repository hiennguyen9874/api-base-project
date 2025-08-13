import casbin
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import forbidden, not_found
from app.src.service import ServiceBase
from app.src.users.services import user_service, UserService

from .. import schemas
from ..errors import (
    author_not_found,
)

__all__ = ["casbin_service", "CasbinService"]


class CasbinService(ServiceBase):
    def __init__(self, user_service: UserService, service_name: str) -> None:
        self.user_service = user_service

    async def get_policy_list(self, enforcer: casbin.AsyncEnforcer) -> list[schemas.Policy]:
        await enforcer.load_policy()
        return [
            schemas.Policy(sub=policy[0], path=policy[1], method=policy[2])
            for policy in enforcer.get_policy()
        ]

    async def get_policy_list_by_role(
        self, enforcer: casbin.AsyncEnforcer, role: str
    ) -> list[schemas.Policy]:
        await enforcer.load_policy()
        return [
            schemas.Policy(sub=policy[0], path=policy[1], method=policy[2])
            for policy in enforcer.get_filtered_named_policy("p", 0, role)
        ]

    async def create_policy(self, enforcer: casbin.AsyncEnforcer, p: schemas.Policy) -> None:
        await enforcer.load_policy()
        if not enforcer.has_policy(p.sub, p.path, p.method):
            await enforcer.add_policy(p.sub, p.path, p.method)

    async def has_policy(self, enforcer: casbin.AsyncEnforcer, p: schemas.Policy) -> bool:
        await enforcer.load_policy()
        return enforcer.has_policy(p.sub, p.path, p.method)

    async def create_policies(
        self, enforcer: casbin.AsyncEnforcer, ps: list[schemas.Policy]
    ) -> None:
        await enforcer.load_policy()
        await enforcer.add_policies([list(p.dict().values()) for p in ps])

    async def update_policy(
        self,
        enforcer: casbin.AsyncEnforcer,
        old: schemas.Policy,
        new: schemas.Policy,
    ) -> None:
        await enforcer.load_policy()
        if not enforcer.has_policy(old.sub, old.path, old.method):
            raise author_not_found(
                msg=f"not found old policy, old.sub: {old.sub}, old.path: {old.path}, old.method: {old.method}"  # noqa: B950,E501
            )
        await enforcer.update_policy(
            [old.sub, old.path, old.method], [new.sub, new.path, new.method]
        )

    async def update_policies(
        self,
        enforcer: casbin.AsyncEnforcer,
        old: list[schemas.Policy],
        new: list[schemas.Policy],
    ) -> None:
        await enforcer.load_policy()
        await enforcer.update_policies(
            [list(o.dict().values()) for o in old],
            [list(n.dict().values()) for n in new],
        )

    async def delete_policy(self, enforcer: casbin.AsyncEnforcer, p: schemas.Policy) -> None:
        await enforcer.load_policy()
        await enforcer.remove_policy(p.sub, p.path, p.method)

    async def delete_policies(
        self, enforcer: casbin.AsyncEnforcer, ps: list[schemas.Policy]
    ) -> None:
        await enforcer.load_policy()
        await enforcer.remove_policies([list(p.dict().values()) for p in ps])

    async def get_group_list(self, enforcer: casbin.AsyncEnforcer) -> list[schemas.Group]:
        await enforcer.load_policy()
        return [
            schemas.Group(sub1=group[0], sub2=group[1]) for group in enforcer.get_grouping_policy()
        ]

    async def create_group(self, enforcer: casbin.AsyncEnforcer, g: schemas.Group) -> None:
        await enforcer.load_policy()
        if not enforcer.has_grouping_policy(g.sub1, g.sub2):
            await enforcer.add_grouping_policy(g.sub1, g.sub2)

    async def create_groups(self, enforcer: casbin.AsyncEnforcer, gs: list[schemas.Group]) -> None:
        await enforcer.load_policy()
        await enforcer.add_grouping_policies([list(g.dict().values()) for g in gs])

    async def delete_group(self, enforcer: casbin.AsyncEnforcer, g: schemas.Group) -> None:
        await enforcer.load_policy()
        await enforcer.remove_grouping_policy(g.sub1, g.sub2)

    async def delete_groups(self, enforcer: casbin.AsyncEnforcer, gs: list[schemas.Group]) -> None:
        await enforcer.load_policy()
        await enforcer.remove_grouping_policies([list(g.dict().values()) for g in gs])

    async def has_grouping(self, enforcer: casbin.AsyncEnforcer, g: schemas.Group) -> bool:
        await enforcer.load_policy()
        return enforcer.has_grouping_policy(g.sub1, g.sub2)

    async def get_all_roles(self, enforcer: casbin.AsyncEnforcer) -> list[str]:
        await enforcer.load_policy()
        return enforcer.get_all_roles()

    async def get_roles_for_user(
        self, db: AsyncSession, enforcer: casbin.AsyncEnforcer, email: str
    ) -> list[str]:
        await enforcer.load_policy()
        if (
            await self.user_service.get_by_email(db=db, cache_connection=None, email=email)
        ) is None:
            raise not_found(f"user not found, email: {email}")

        return await enforcer.get_implicit_roles_for_user(name=email)

    async def get_users_for_role(self, enforcer: casbin.AsyncEnforcer, role: str) -> list[str]:
        await enforcer.load_policy()
        return await enforcer.get_users_for_role(name=role)

    async def add_role_for_user(
        self,
        db: AsyncSession,
        enforcer: casbin.AsyncEnforcer,
        email: str,
        role: str,
        available_roles: list[str] | None = None,
    ) -> None:
        await enforcer.load_policy()
        if available_roles is not None and role not in available_roles:
            raise forbidden("user doesn't have enough privileges to add role")

        if (
            await self.user_service.get_by_email(db=db, cache_connection=None, email=email)
        ) is None:
            raise not_found(f"user not found, email: {email}")

        if not await enforcer.has_role_for_user(name=email, role=role):
            await enforcer.add_role_for_user(user=email, role=role)

    async def has_role_for_user(
        self,
        db: AsyncSession,
        enforcer: casbin.AsyncEnforcer,
        email: str,
        role: str,
        available_roles: list[str] | None = None,
    ) -> None:
        await enforcer.load_policy()
        if available_roles is not None and role not in available_roles:
            raise forbidden("user doesn't have enough privileges to add role")

        if (
            await self.user_service.get_by_email(db=db, cache_connection=None, email=email)
        ) is None:
            raise not_found(f"user not found, email: {email}")

        await enforcer.has_role_for_user(name=email, role=role)

    async def delete_role_for_user(
        self,
        db: AsyncSession,
        enforcer: casbin.AsyncEnforcer,
        email: str,
        role: str,
    ) -> None:
        await enforcer.load_policy()
        if (
            await self.user_service.get_by_email(db=db, cache_connection=None, email=email)
        ) is None:
            raise not_found(f"user not found, email: {email}")

        await enforcer.delete_role_for_user(user=email, role=role)


casbin_service = CasbinService(user_service=user_service, service_name="casbin")
