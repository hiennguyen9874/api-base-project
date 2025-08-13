from typing import Any, Awaitable, Callable, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException
from starlette.websockets import WebSocket

from app import errors
from app.schemas.response import Error, ErrorResponse, Status, ValidationErrorResponse

# Define handler types to match FastAPI's expected types
ExceptionHandler = Callable[[Request, Exception], Awaitable[Response] | Response]
WebSocketExceptionHandler = Callable[[WebSocket, Exception], Awaitable[None]]


async def app_exception_handler(request: Request, exc: errors.AppException) -> JSONResponse:
    """Handler for AppException errors."""
    response_body = ErrorResponse[str](
        status=Status.error,
        error=Error[str](code=str(exc.status_text), message=str(exc.msg)),
        data=exc.details,
    ).model_dump()

    return JSONResponse(
        content=response_body,
        status_code=exc.status_code,
    )


async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """Handler for validation errors."""
    return JSONResponse(
        content=ValidationErrorResponse[list[dict[str, Any]]](
            status=Status.error,
            error=Error[list[dict[str, Any]]](code="422", message=exc.errors()),
            data=None,
        ).model_dump(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTP exceptions."""
    return JSONResponse(
        content=ErrorResponse[str](
            status=Status.error,
            error=Error[str](code=str(exc.status_code), message=str(exc.detail)),
            data=None,
        ).model_dump(),
        status_code=exc.status_code,
    )


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handler for rate limit exceeded errors."""
    return JSONResponse(
        content=ErrorResponse[str](
            status=Status.error,
            error=Error[str](code="429", message="Too Many Requests"),
            data=None,
        ).model_dump(),
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers to the FastAPI application.

    FastAPI expects handlers that can return either Response or Awaitable[Response].
    Our async handlers are compatible with this requirement.
    """
    app.add_exception_handler(errors.AppException, app_exception_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(ValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore
    app.add_exception_handler(429, rate_limit_exceeded_handler)  # type: ignore
