from pathlib import Path
from typing import Annotated

from pydantic import AnyUrl, BaseModel, BeforeValidator

from .common_validators import parse_cors_origin, parse_trusted_host


class AppSettings(BaseModel):
    NAME: str = "fastapi-base-project"
    VERSION: str = "0.0.1"
    TIMEZONE: str = "Asia/Ho_Chi_Minh"
    SECRET_KEY: str = "secretsecretsecret"
    API_PREFIX: str = "/api"

    BASE_DIR: Path = Path("/app")
    CONFIG_DIR: Path = Path("/app/app/configs")
    STATIC_DIR: Path = Path("/app/app/static")

    MEDIA_ROOT: Path = Path("/app/media")
    MEDIA_URL: str = "/media"
    PROTECT_MEDIA: bool = False

    VIDEO_FOLDER: str = "videos"
    ZM_FOLDER: str = "ZM"
    ZM_ENCODED_FOLDER: str = "ZM-Encoded"
    EXPORT_FOLDER: str = "export"

    ENABLE_DOCS: bool = True

    CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors_origin)]
    TRUSTED_HOST: Annotated[list[str] | str, BeforeValidator(parse_trusted_host)]
