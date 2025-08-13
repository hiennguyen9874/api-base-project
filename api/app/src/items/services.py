from typing import Any, Sequence, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.src.service import ServiceBase

from .db_models import Item
from .db_repository import item_db_repository, ItemDbRepository
from .schemas import ItemCreate, ItemUpdate


class ItemService(ServiceBase):
    def __init__(
        self, model: Type[Item], db_repository: ItemDbRepository, service_name: str
    ) -> None:
        self.model = model
        self.db_repository = db_repository

    ## Create

    async def create(self, db: AsyncSession, obj_in: ItemCreate) -> Item:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        return await self.db_repository.create(db=db, db_obj=db_obj)

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)  # type: ignore
        return await self.db_repository.create(db=db, db_obj=db_obj)

    ## Get all

    async def get_all(self, db: AsyncSession) -> Sequence[Item]:
        return await self.db_repository.get_all(db=db)

    ## Get multi

    async def get_multi(
        self, db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> Sequence[Item]:
        return await self.db_repository.get_multi(db=db, offset=offset, limit=limit)

    async def get_multi_count(
        self, db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Item], int]:
        return await self.db_repository.get_multi_count(db=db, offset=offset, limit=limit)

    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Item]:
        return await self.db_repository.get_multi_by_owner(
            db=db, owner_id=owner_id, offset=offset, limit=limit
        )

    async def get_multi_by_owner_count(
        self, db: AsyncSession, *, owner_id: int, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Item], int]:
        items = await self.db_repository.get_multi_by_owner(
            db=db, owner_id=owner_id, offset=offset, limit=limit
        )
        total = await self.db_repository.count_by_owner(db=db, owner_id=owner_id)
        return items, total

    ## Get one
    async def get(
        self,
        db: AsyncSession,
        id: int,  # pylint: disable=redefined-builtin
    ) -> Item | None:
        return await self.db_repository.get(db=db, id=id)

    ## Delete

    async def delete(self, db: AsyncSession, db_obj: Item) -> None:
        await self.db_repository.delete(db=db, db_obj=db_obj)

    async def delete_by_id(
        self,
        db: AsyncSession,
        id: int,  # pylint: disable=redefined-builtin
    ) -> None:
        await self.db_repository.delete_by_id(db=db, id=id)

    ## Update

    async def update(
        self, db: AsyncSession, db_obj: Item, obj_in: ItemUpdate | dict[str, Any]
    ) -> Item:
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data=(obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)),
        )


item_service = ItemService(model=Item, db_repository=item_db_repository, service_name="item")
