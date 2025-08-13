from pydantic import BaseModel, ConfigDict

from app.schemas import OptionalField

__all__ = [
    "CasbinRule",
    "CasbinRuleCreate",
    "CasbinRuleUpdate",
    "CasbinRuleInDB",
    "Policy",
    "Group",
    "GetAllPolicy",
]


class CasbinRuleBase(BaseModel):
    ptype: OptionalField[str] = None
    v0: OptionalField[str] = None
    v1: OptionalField[str] = None
    v2: OptionalField[str] = None
    v3: OptionalField[str] = None
    v4: OptionalField[str] = None
    v5: OptionalField[str] = None


# Properties to receive on item creation
class CasbinRuleCreate(CasbinRuleBase):
    pass


# Properties to receive on item update
class CasbinRuleUpdate(CasbinRuleBase):
    pass


# Properties shared by models stored in DB
class CasbinRuleInDBBase(CasbinRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CasbinRuleInDB(CasbinRuleInDBBase):
    pass


# Properties to return to client
class CasbinRule(CasbinRuleInDBBase):
    model_config = ConfigDict(from_attributes=True)


class Policy(BaseModel):
    sub: str
    path: str
    method: str
    model_config = ConfigDict(use_enum_values=True)


class Group(BaseModel):
    sub1: str
    sub2: str

    model_config = ConfigDict(use_enum_values=True)


class GetAllPolicy(BaseModel):
    id: int
    ptype: str
    v0: str
    v1: str
    v2: OptionalField[str] = None
    v3: OptionalField[str] = None
    v4: OptionalField[str] = None
    v5: OptionalField[str] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
