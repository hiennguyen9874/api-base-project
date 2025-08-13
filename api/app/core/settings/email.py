from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationInfo


class EmailSettings(BaseModel):
    TEMPLATES_DIR: str = "/app/app/email-templates/build"

    # Smtp
    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    # From
    FROM_EMAIL: EmailStr | None = None
    FROM_NAME: str | None = None

    # Reset token
    RESET_TOKEN_ALGORITHM: str = "HS256"
    RESET_TOKEN_SECRET_KEY: str = "secretsecretsecret"
    RESET_TOKEN_EXPIRE_DURATION: int = 60
    RESET_TOKEN_EXPIRE_HOURS: int = 1

    # Project
    SERVER_HOST: str | None = None
    PROJECT_NAME: str = "fastapi-base-project"

    ENABLED: Annotated[bool, Field(validate_default=True)] = False

    @field_validator("ENABLED", mode="after")
    @classmethod
    def get_email_enabled(cls, v: bool, info: ValidationInfo) -> bool:
        return bool(
            info.data["SMTP_USER"]
            and info.data["SMTP_PASSWORD"]
            and info.data["SMTP_PORT"]
            and info.data["SMTP_HOST"]
            and info.data["FROM_EMAIL"]
            and info.data["FROM_NAME"]
        )
