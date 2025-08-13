from typing import Sequence

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.src.db_repository import BaseDbRepository

from .db_models import CasbinRule


class CasbinRuleDbRepository(BaseDbRepository[CasbinRule]):
    ### Get
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
        query = (
            select(self.model)
            .where(self.model.ptype == ptype)
            .where(self.model.v0 == v0)
            .where(self.model.v1 == v1)
            .where(self.model.v2 == v2)
            .where(self.model.v3 == v3)
            .where(self.model.v4 == v4)
            .where(self.model.v5 == v5)
        )
        q = await db.execute(query)
        return q.scalars().one_or_none()

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
        query = select(self.model)
        if ptype:
            query = query.where(self.model.ptype.in_(list(ptype)))
        if v0:
            query = query.where(self.model.v0.in_(list(v0)))
        if v1:
            query = query.where(self.model.v1.in_(list(v1)))
        if v2:
            query = query.where(self.model.v2.in_(list(v2)))
        if v3:
            query = query.where(self.model.v3.in_(list(v3)))
        if v4:
            query = query.where(self.model.v4.in_(list(v4)))
        if v5:
            query = query.where(self.model.v5.in_(list(v5)))
        q = await db.execute(query)
        return q.scalars().all()

    ### Delete
    async def delete_all(self, db: AsyncSession) -> None:
        await db.execute(delete(self.model))
        await db.commit()

    async def delete_by_attribute(
        self,
        db: AsyncSession,
        *,
        ptype: str | None = None,
        v0: str | None = None,
        v1: str | None = None,
        v2: str | None = None,
        v3: str | None = None,
        v4: str | None = None,
        v5: str | None = None,
    ) -> bool:
        query = delete(self.model)
        if ptype is not None:
            query = query.where(self.model.ptype == ptype)
        if v0 is not None:
            query = query.where(self.model.v0 == v0)
        if v1 is not None:
            query = query.where(self.model.v1 == v1)
        if v2 is not None:
            query = query.where(self.model.v2 == v2)
        if v3 is not None:
            query = query.where(self.model.v3 == v3)
        if v4 is not None:
            query = query.where(self.model.v4 == v4)
        if v5 is not None:
            query = query.where(self.model.v5 == v5)
        result = await db.execute(query)
        await db.commit()
        return True if result.rowcount > 0 else False

    ### Update

    async def update_by_attribute(  # noqa: C901
        self,
        db: AsyncSession,
        db_objs: list[CasbinRule],
        *,
        ptype: str | None = None,
        v0: str | None = None,
        v1: str | None = None,
        v2: str | None = None,
        v3: str | None = None,
        v4: str | None = None,
        v5: str | None = None,
    ) -> None:
        query = delete(self.model)
        if ptype is not None:
            query = query.where(self.model.ptype == ptype)
        if v0 is not None:
            query = query.where(self.model.v0 == v0)
        if v1 is not None:
            query = query.where(self.model.v1 == v1)
        if v2 is not None:
            query = query.where(self.model.v2 == v2)
        if v3 is not None:
            query = query.where(self.model.v3 == v3)
        if v4 is not None:
            query = query.where(self.model.v4 == v4)
        if v5 is not None:
            query = query.where(self.model.v5 == v5)
        await db.execute(query)
        await db.flush()
        for db_obj in db_objs:
            db.add(db_obj)
        await db.commit()

    ### Save = delete all + all
    async def save(self, db: AsyncSession, *, db_objs: list[CasbinRule]) -> None:
        await db.execute(delete(self.model))
        await db.flush()
        for db_obj in db_objs:
            db.add(db_obj)
        await db.commit()


casbin_rule_db_repository = CasbinRuleDbRepository(model=CasbinRule)
