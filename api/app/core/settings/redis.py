from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator, RedisDsn, ValidationInfo


class RedisLockSettings(BaseModel):
    HOST: str = "redis"
    PORT: int = 6379
    DB: int = 2

    API_MAX_CONNECTIONS: int = 20
    WORKER_MAX_CONNECTIONS: int = 10


class RedisCacheSettings(BaseModel):
    HOST: str = "redis"
    PORT: int = 6379
    DB: int = 2

    API_MAX_CONNECTIONS: int = 20
    WORKER_MAX_CONNECTIONS: int = 10

    URL: Annotated[RedisDsn | None, Field(validate_default=True)] = None

    @field_validator("URL", mode="after")
    @classmethod
    def assemble_redis_stack_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return RedisDsn.build(
            scheme="redis",
            host=info.data["HOST"],  # type: ignore
            port=info.data["PORT"],
            path=str(info.data["DB"]),
        )

    USER_TTL: int = 60 * 60
    CASBIN_TTL: int = 60 * 60
