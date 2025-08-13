from pydantic import BaseModel


class TaskiqSettings(BaseModel):
    BROKER_URL: str
    RESULT_BACKEND: str
