from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.settings import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{settings.RATELIMIT.REDIS_HOST}:{settings.RATELIMIT.REDIS_PORT}/{settings.RATELIMIT.REDIS_DB}",
)
