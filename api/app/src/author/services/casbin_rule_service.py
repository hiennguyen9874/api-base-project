from typing import Any, Sequence, Type

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.service import ServiceBase

from .. import schemas
from ..cache_repository import casbin_rule_cache_repository, CasbinRuleCacheRepository
from ..db_models import CasbinRule
from ..db_repository import casbin_rule_db_repository, CasbinRuleDbRepository

__all__ = ["casbin_rule_service", "CasbinRuleService"]


class CasbinRuleService(ServiceBase):
    def __init__(
        self,
        model: Type[CasbinRule],
        db_repository: CasbinRuleDbRepository,
        cache_repository: CasbinRuleCacheRepository,
        service_name: str,
    ) -> None:
        self.model = model
        self.db_repository = db_repository
        self.cache_repository = cache_repository

    ## Create

    async def create(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        obj_in: schemas.CasbinRuleCreate,
    ) -> CasbinRule:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        return await self.db_repository.create(db=db, db_obj=db_obj)

    async def creates(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        objs_in: list[schemas.CasbinRuleCreate],
    ) -> None:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        await self.db_repository.creates(
            db=db,
            db_objs=[self.model(**obj_in.model_dump(exclude_unset=True)) for obj_in in objs_in],
        )

    ## Get all

    async def get_all(
        self, db: AsyncSession, cache_connection: Redis
    ) -> Sequence[CasbinRule] | None:
        cached_casbin_rules = await self.cache_repository.get_cache_all(connection=cache_connection)
        if cached_casbin_rules is not None:
            return cached_casbin_rules
        casbin_rules = await self.db_repository.get_all(db=db)
        if not casbin_rules:
            return None
        await self.cache_repository.create_cache_all(
            connection=cache_connection, obj_casbin_rules=casbin_rules
        )
        return casbin_rules

    async def get_all_by_list_attribute(
        self,
        db: AsyncSession,
        *,
        ptype: list[str] | None = None,
        v0: list[str] | None = None,
        v1: list[str] | None = None,
        v2: list[str] | None = None,
        v3: list[str] | None = None,
        v4: list[str] | None = None,
        v5: list[str] | None = None,
    ) -> Sequence[CasbinRule]:
        return await self.db_repository.get_all_by_list_attribute(
            db=db,
            ptype=ptype,
            v0=v0,
            v1=v1,
            v2=v2,
            v3=v3,
            v4=v4,
            v5=v5,
        )

    ## Get multi

    async def get_multi(
        self, db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> Sequence[CasbinRule]:
        return await self.db_repository.get_multi(db=db, offset=offset, limit=limit)

    async def get_multi_count(
        self, db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[CasbinRule], int]:
        return await self.db_repository.get_multi_count(db=db, offset=offset, limit=limit)

    ## Get one
    async def get(
        self,
        db: AsyncSession,
        id: int,  # pylint: disable=redefined-builtin
    ) -> CasbinRule | None:
        return await self.db_repository.get(db=db, id=id)

    async def get_by_attribute(
        self,
        db: AsyncSession,
        *,
        ptype: str,
        v0: str | None = None,
        v1: str | None = None,
        v2: str | None = None,
        v3: str | None = None,
        v4: str | None = None,
        v5: str | None = None,
    ) -> CasbinRule | None:
        return await self.db_repository.get_by_attribute(
            db=db,
            ptype=ptype,
            v0=v0,
            v1=v1,
            v2=v2,
            v3=v3,
            v4=v4,
            v5=v5,
        )

    ## Delete

    async def delete(self, db: AsyncSession, cache_connection: Redis, db_obj: CasbinRule) -> None:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        await self.db_repository.delete(db=db, db_obj=db_obj)

    async def delete_by_id(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        id: int,  # pylint: disable=redefined-builtin
    ) -> None:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        await self.db_repository.delete_by_id(db=db, id=id)

    async def delete_all(self, db: AsyncSession, cache_connection: Redis) -> None:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        await self.db_repository.delete_all(db=db)

    async def delete_by_attribute(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        *,
        ptype: str | None = None,
        v0: str | None = None,
        v1: str | None = None,
        v2: str | None = None,
        v3: str | None = None,
        v4: str | None = None,
        v5: str | None = None,
    ) -> bool:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        return await self.db_repository.delete_by_attribute(
            db=db,
            ptype=ptype,
            v0=v0,
            v1=v1,
            v2=v2,
            v3=v3,
            v4=v4,
            v5=v5,
        )

    ## Update

    async def update(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        db_obj: CasbinRule,
        obj_in: schemas.CasbinRuleUpdate | dict[str, Any],
    ) -> CasbinRule:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data=(obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)),
        )

    async def update_by_attribute(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        objs_in: list[schemas.CasbinRuleCreate],
        *,
        ptype: str | None = None,
        v0: str | None = None,
        v1: str | None = None,
        v2: str | None = None,
        v3: str | None = None,
        v4: str | None = None,
        v5: str | None = None,
    ) -> None:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        await self.db_repository.update_by_attribute(
            db=db,
            db_objs=[self.model(**obj_in.model_dump(exclude_unset=True)) for obj_in in objs_in],
            ptype=ptype,
            v0=v0,
            v1=v1,
            v2=v2,
            v3=v3,
            v4=v4,
            v5=v5,
        )

    ### Save = delete all + adds
    async def save(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        *,
        objs_in: list[schemas.CasbinRuleCreate],
    ) -> None:
        await self.cache_repository.delete_cache_all(connection=cache_connection)
        await self.db_repository.save(
            db=db,
            db_objs=[self.model(**obj_in.model_dump(exclude_unset=True)) for obj_in in objs_in],
        )


casbin_rule_service = CasbinRuleService(
    model=CasbinRule,
    db_repository=casbin_rule_db_repository,
    cache_repository=casbin_rule_cache_repository,
    service_name="casbin_rule",
)
