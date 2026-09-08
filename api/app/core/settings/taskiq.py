from pydantic import BaseModel


class TaskiqSettings(BaseModel):
    BROKER_URL: str = "amqp://guest:guest@localhost:5672"
    RESULT_BACKEND: str = "redis://localhost:6379/0"
