from pydantic import BaseModel


class RateLimitSettings(BaseModel):
    REDIS_HOST: str = "redis-cache"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 3

    LOGIN_RATELIMIT1: str = "100/5minute"
    LOGIN_RATELIMIT2: str = "1000/hour"
