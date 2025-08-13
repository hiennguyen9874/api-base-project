from pydantic import BaseModel, ConfigDict

from app.schemas import OptionalField

__all__ = ["Item", "ItemCreate", "ItemUpdate"]


class ItemBase(BaseModel):
    title: OptionalField[str] = None
    description: OptionalField[str] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    # owner: UserInDBBase


# Properties to return to client
class Item(ItemInDBBase):
    model_config = ConfigDict(from_attributes=True)

    # owner: User
