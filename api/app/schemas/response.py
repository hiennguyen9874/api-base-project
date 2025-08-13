from enum import Enum
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, Field

from app.schemas import OptionalField

DataT = TypeVar("DataT")
ErrorT = TypeVar("ErrorT")


__all__ = [
    "Error",
    "Status",
    "ErrorResponse",
    "SuccessfulResponse",
    "create_successful_response",
    "ValidationErrorResponse",
]


class Error(BaseModel, Generic[ErrorT]):
    code: str
    message: Annotated[ErrorT, Field(examples=["Error message"])]

    __hash__ = object.__hash__


class Status(str, Enum):
    success = "success"
    error = "error"


class ErrorResponse(BaseModel, Generic[ErrorT]):
    status: Status = Status.error
    error: Annotated[Error[ErrorT], Field(examples=[{"code": "400", "message": "Error message"}])]
    data: Annotated[OptionalField[Any], Field(examples=["null"])] = None

    __hash__ = object.__hash__


class ValidationErrorResponse(BaseModel, Generic[ErrorT]):
    status: Status = Status.error
    error: Annotated[
        Error[ErrorT],
        Field(
            examples=[
                {"code": "422", "message": [{"loc": ["string"], "msg": "string", "type": "string"}]}
            ]
        ),
    ]
    data: Annotated[OptionalField[Any], Field(examples=["null"])] = None

    __hash__ = object.__hash__


class SuccessfulResponse(BaseModel, Generic[DataT]):
    status: Status = Status.success
    data: OptionalField[DataT] = None
    error: Annotated[OptionalField[Any], Field(examples=["null"])] = None

    __hash__ = object.__hash__


def create_successful_response(data: DataT) -> SuccessfulResponse[DataT]:
    return SuccessfulResponse(data=data, error=None, status=Status.success)
