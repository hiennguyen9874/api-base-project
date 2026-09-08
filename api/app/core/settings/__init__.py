import os
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Type

from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

from .app import AppSettings
from .database import PostgresSettings, SQLAlchemySettings
from .email import EmailSettings
from .monitoring import SentrySettings
from .ratelimit import RateLimitSettings
from .redis import RedisCacheSettings, RedisLockSettings
from .taskiq import TaskiqSettings
from .tasks import TasksSettings
from .token import TokenSettings
from .user import UserSettings

__all__ = ["settings", "get_settings"]

YAML_FILE_PATH = Path(
    os.getenv(
        "APP_CONFIG_FILE",
        Path(__file__).resolve().parents[2] / "configs" / "config.yml",
    )
)


class CashLensEnvSettingsSource(EnvSettingsSource):
    """Read app environment variables without the shell's bare ``USER`` value."""

    def _load_env_vars(self) -> Mapping[str, str | None]:
        env_vars = super()._load_env_vars()
        # ``USER`` is normally the host account name (for example, ``hiennx``),
        # while the application uses USER as a nested settings section. A bare
        # value would be decoded as JSON before the YAML fallback is considered.
        return {key: value for key, value in env_vars.items() if key != "user"}


class Settings(BaseSettings):
    APP: AppSettings
    RATELIMIT: RateLimitSettings = RateLimitSettings()
    TOKEN: TokenSettings
    EMAIL: EmailSettings = EmailSettings()
    POSTGRES: PostgresSettings
    SQLALCHEMY: SQLAlchemySettings = SQLAlchemySettings()
    SENTRY: SentrySettings = SentrySettings()
    USER: UserSettings
    REDIS_CACHE: RedisCacheSettings = RedisCacheSettings()
    REDIS_LOCK: RedisLockSettings = RedisLockSettings()
    TASKS: TasksSettings = TasksSettings()
    TASKIQ: TaskiqSettings = TaskiqSettings()

    @classmethod
    def settings_customise_sources(  # type: ignore
        cls, settings_cls: Type[BaseSettings], **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            CashLensEnvSettingsSource(
                settings_cls,
                env_nested_delimiter="__",
                env_parse_none_str="null",
                case_sensitive=False,
            ),
            YamlConfigSettingsSource(settings_cls, yaml_file=YAML_FILE_PATH),
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
