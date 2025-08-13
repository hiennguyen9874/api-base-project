from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.optional import OptionalField

__all__ = [
    "User",
    "UserCreate",
    "UserInDB",
    "UserUpdate",
    "UserLogin",
    "UserUpdateMe",
    "UserCreateOpen",
]


class UserBase(BaseModel):
    email: OptionalField[EmailStr] = None
    is_active: OptionalField[bool] = True
    full_name: OptionalField[str] = None
    avatar_url: OptionalField[str] = None
    default_currency: OptionalField[str] = "VND"
    language_preference: OptionalField[str] = "vi-VN"
    account_status: OptionalField[str] = "ACTIVE"


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on creation for open registration
class UserCreateOpen(UserCreate):
    default_currency: OptionalField[str] = "VND"
    language_preference: OptionalField[str] = "vi-VN"


# Properties to receive via API on Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: OptionalField[str] = None
    email: OptionalField[EmailStr] = None
    full_name: OptionalField[str] = None
    avatar_url: OptionalField[str] = None
    default_currency: OptionalField[str] = None
    language_preference: OptionalField[str] = None
    account_status: OptionalField[str] = None


# Properties to receive via API on update for current user
class UserUpdateMe(BaseModel):
    password: OptionalField[str] = None
    full_name: OptionalField[str] = None
    avatar_url: OptionalField[str] = None
    default_currency: OptionalField[str] = None
    language_preference: OptionalField[str] = None


class UserInDBBase(UserBase):
    id: OptionalField[int] = None
    email: OptionalField[EmailStr] = None
    registration_date: OptionalField[datetime] = None
    last_login_date: OptionalField[datetime] = None
    two_factor_enabled: OptionalField[bool] = False
    two_factor_secret: OptionalField[str] = None
    model_config = ConfigDict(from_attributes=True)


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: OptionalField[str] = None
