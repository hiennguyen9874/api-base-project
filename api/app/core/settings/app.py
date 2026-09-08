from pathlib import Path
from typing import Annotated

from pydantic import AnyUrl, BaseModel, BeforeValidator, Field

from .common_validators import parse_cors_origin, parse_trusted_host
from .development import ephemeral_development_secret

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class AppSettings(BaseModel):
    NAME: str = "CashLens"
    VERSION: str = "0.0.1"
    TIMEZONE: str = "Asia/Ho_Chi_Minh"
    SECRET_KEY: str = Field(default_factory=ephemeral_development_secret, min_length=32)
    API_PREFIX: str = "/api"

    # Resolves to /app in the container and api/ when imported from a checkout.
    BASE_DIR: Path = PROJECT_ROOT
    CONFIG_DIR: Path = PROJECT_ROOT / "app" / "configs"
    STATIC_DIR: Path = PROJECT_ROOT / "app" / "static"

    MEDIA_ROOT: Path = PROJECT_ROOT / "media"
    MEDIA_URL: str = "/media"
    PROTECT_MEDIA: bool = False

    VIDEO_FOLDER: str = "videos"
    ZM_FOLDER: str = "ZM"
    ZM_ENCODED_FOLDER: str = "ZM-Encoded"
    EXPORT_FOLDER: str = "export"

    ENABLE_DOCS: bool = True

    CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors_origin)]
    TRUSTED_HOST: Annotated[list[str] | str, BeforeValidator(parse_trusted_host)]
