from typing import ParamSpec, TypeVar

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class ServiceBase:
    def __init__(self) -> None:
        pass
