from pydantic import BaseModel, EmailStr, Field

from .development import ephemeral_development_secret


class UserSettings(BaseModel):
    OPEN_REGISTRATION: bool = False

    FIRST_USER_EMAIL: EmailStr = "owner@example.com"
    FIRST_USER_PASSWORD: str = Field(default_factory=ephemeral_development_secret)
    FIRST_USER_FULL_NAME: str = "admin"
