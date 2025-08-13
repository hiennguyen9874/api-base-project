from pydantic import BaseModel, EmailStr

from app.schemas import OptionalField

__all__ = ["Token", "TokenPayload", "OIDCUser"]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str


class OIDCUser(BaseModel):
    # active: OptionalField[bool] = True
    # iss: str
    # azp: str
    # aud: str
    sub: str
    # typ: str
    # iat: str
    # exp: str

    # jti: OptionalField[str]
    email: EmailStr
    name: OptionalField[str] = None
    username: OptionalField[str] = None
    preferred_username: OptionalField[str] = None
    # client_id: OptionalField[str]
    # sid: OptionalField[str]
    # scope: OptionalField[str]
    # session_state: OptionalField[str]
    email_verified: OptionalField[bool] = None
    # acr: OptionalField[str]
    # realm_access: dict[str, list[str]]
    # resource_access: dict[str, dict[str, list[str]]]
    # allowed_origins: OptionalField[list[str]] = Field(alias="allowed-origins")
