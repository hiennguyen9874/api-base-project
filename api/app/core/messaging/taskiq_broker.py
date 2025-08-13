from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from app.core.settings import settings

broker = AioPikaBroker(
    settings.TASKIQ.BROKER_URL,
).with_result_backend(RedisAsyncResultBackend(settings.TASKIQ.RESULT_BACKEND))
