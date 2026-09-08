from typing import Literal

from pydantic import BaseModel, Field

from .development import ephemeral_development_secret


class TokenSettings(BaseModel):
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_SECRET_KEY: str = Field(
        default_factory=ephemeral_development_secret, min_length=32
    )
    ACCESS_TOKEN_EXPIRE_DURATION: int = 60 * 24 * 8

    REFRESH_TOKEN_SECRET_KEY: str = Field(
        default_factory=ephemeral_development_secret, min_length=32
    )
    REFRESH_TOKEN_EXPIRE_DURATION: int = 60 * 24 * 15

    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] | None = "none"
