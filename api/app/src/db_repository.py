from typing import Any, Generic, ParamSpec, Sequence, Type, TypeVar

from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from .db_base import Base

ModelType = TypeVar("ModelType", bound=Base)
Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class BaseDbRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    ## Create

    async def create(
        self, db: AsyncSession, *, db_obj: ModelType, commit: bool = True
    ) -> ModelType:
        db.add(db_obj)
        if commit:
            await db.commit()
        else:
            await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def creates(
        self, db: AsyncSession, *, db_objs: list[ModelType], commit: bool = True
    ) -> None:
        for db_obj in db_objs:
            db.add(db_obj)
        if commit:
            await db.commit()

    ## Get multi

    async def get_multi(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        query = select(self.model).offset(offset).limit(limit).order_by(self.model.id)
        q = await db.execute(query)
        return q.scalars().all()

    async def get_multi_count(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[ModelType], int]:
        items = await self.get_multi(db, offset=offset, limit=limit)
        total = await self.count_all(db)
        return items, total

    ## Get all

    async def get_all(self, db: AsyncSession) -> Sequence[ModelType]:
        query = select(self.model).order_by(self.model.id)
        q = await db.execute(query)
        return q.scalars().all()

    ## Get one

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        q = await db.execute(select(self.model).where(self.model.id == id))
        return q.scalars().one_or_none()

    ## Count

    async def count(self, db: AsyncSession, query: Select) -> int:
        """Counting of results returned by the query

        Args:
            db (AsyncSession): AsyncSession
            query (Select): query

        Returns:
            int: Number of results returned by the query
        """
        return await db.scalar(
            select(func.count()).select_from(
                query.with_only_columns(self.model.id).subquery()  # type: ignore
            )
        )

    async def count_all(self, db: AsyncSession) -> int:
        return await self.count(db=db, query=select(self.model))

    ## Delete

    async def delete_by_id(self, db: AsyncSession, *, id: int) -> ModelType | None:
        q = await db.execute(select(self.model).where(self.model.id == id))
        obj = q.scalar_one()
        await db.delete(obj)
        await db.commit()
        return obj

    async def delete(self, db: AsyncSession, *, db_obj: ModelType, commit: bool = True) -> None:
        await db.delete(db_obj)
        if commit:
            await db.commit()
        else:
            await db.flush()

    ## Update

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        update_data: dict[str, Any],
        commit: bool = True,
    ) -> ModelType:
        query = update(self.model).where(self.model.id == db_obj.id).values(update_data)
        await db.execute(query)
        if commit:
            await db.commit()
        else:
            await db.flush()
        await db.refresh(db_obj)
        return db_obj
