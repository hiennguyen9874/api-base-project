from functools import cached_property
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    computed_field,
    Field,
    field_validator,
    PostgresDsn,
    ValidationInfo,
)

from .development import ephemeral_development_secret


class PostgresSettings(BaseModel):
    HOST: str = "db"
    PORT: int = 5432
    USER: str = "cashlens"
    PASSWORD: str = Field(default_factory=ephemeral_development_secret)
    DB: str = "cashlens"
    DATABASE_URI: Annotated[PostgresDsn | None, Field(validate_default=True)] = None

    @field_validator("DATABASE_URI", mode="after")
    @classmethod
    def assemble_db_connection(  # pylint: disable=no-self-argument
        cls, v: str | None, info: ValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data["USER"],
            password=info.data["PASSWORD"],
            host=info.data["HOST"],  # type: ignore
            port=info.data["PORT"],
            path=str(info.data["DB"]) or "",
        )

    @computed_field(return_type=str)  # type: ignore[misc]
    @cached_property
    def ASYNC_DATABASE_URI(self) -> str:
        if not self.DATABASE_URI:
            raise RuntimeError("DATABASE_URI must be not None")

        return (
            str(self.DATABASE_URI).replace("postgresql://", "postgresql+asyncpg://")
            if self.DATABASE_URI
            else str(self.DATABASE_URI)
        )


class SQLAlchemySettings(BaseModel):
    ECHO: bool = False
