from functools import lru_cache
from typing import Type

from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

from .api import ApiSettings
from .app import AppSettings
from .casbin import CasbinSettings
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

YAML_FILE_PATH = "/app/app/configs/config.yml"


class Settings(BaseSettings):
    APP: AppSettings
    API: ApiSettings = ApiSettings()
    RATELIMIT: RateLimitSettings = RateLimitSettings()
    TOKEN: TokenSettings = TokenSettings()
    EMAIL: EmailSettings = EmailSettings()
    POSTGRES: PostgresSettings
    SQLALCHEMY: SQLAlchemySettings = SQLAlchemySettings()
    SENTRY: SentrySettings = SentrySettings()
    USER: UserSettings
    REDIS_CACHE: RedisCacheSettings = RedisCacheSettings()
    REDIS_LOCK: RedisLockSettings = RedisLockSettings()
    CASBIN: CasbinSettings = CasbinSettings()
    TASKS: TasksSettings = TasksSettings()
    TASKIQ: TaskiqSettings

    @classmethod
    def settings_customise_sources(  # type: ignore
        cls, settings_cls: Type[BaseSettings], **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            EnvSettingsSource(
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
