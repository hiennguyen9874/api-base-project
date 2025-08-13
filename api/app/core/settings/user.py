from pydantic import BaseModel, EmailStr


class UserSettings(BaseModel):
    OPEN_REGISTRATION: bool = False

    FIRST_USER_EMAIL: EmailStr
    FIRST_USER_PASSWORD: str
    FIRST_USER_FULL_NAME: str = "admin"
    FIRST_USER_ROLE: str = "role:superuser"
