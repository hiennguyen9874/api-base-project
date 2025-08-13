from pydantic import BaseModel

__all__ = ["Msg"]


class Msg(BaseModel):
    msg: str
