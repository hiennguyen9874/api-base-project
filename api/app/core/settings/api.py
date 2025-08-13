from pydantic import BaseModel


class ApiSettings(BaseModel):
    CREATE_CACHE_OBJECT_IMAGE: bool = True
