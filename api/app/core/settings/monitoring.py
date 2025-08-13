from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    HttpUrl,
)


class SentrySettings(BaseModel):
    DSN: Annotated[HttpUrl | None, Field(validate_default=True)] = None
    ENVIRONMENT: str | None = None
    ENABLE_TRACING: bool = False
    TRACES_SAMPLE_RATE: float = 0.0

    @field_validator("DSN", mode="after")
    @classmethod
    def sentry_dsn_can_be_blank(cls, v: str | None) -> str | None:  # pylint: disable=no-self-argument
        return v or None
