from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.src.db_repository import BaseDbRepository

from .db_models import Item


class ItemDbRepository(BaseDbRepository[Item]):
    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Item]:
        q = await db.execute(
            select(self.model)
            .where(self.model.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
            .order_by(self.model.id)
        )
        return q.scalars().all()

    async def count_by_owner(self, db: AsyncSession, *, owner_id: int) -> int:
        return await self.count(
            db=db, query=select(self.model).where(self.model.owner_id == owner_id)
        )


item_db_repository = ItemDbRepository(model=Item)
