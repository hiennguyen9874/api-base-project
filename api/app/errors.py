from enum import Enum
from typing import Any, Optional

from fastapi import status

__all__ = [
    # Main exception class
    "AppException",
    # Error code enum
    "ErrorCode",
    # Utility functions
    "bad_request",
    "not_found",
    "unauthorized",
    "internal_server_error",
    "request_timeout",
    "validation_error",
    "forbidden",
    "make_request_error",
    "call_request_error",
    "read_body_request_error",
    "api_disabled",
    "read_uploaded_file_error",
    "validation_datetime_error",
]


class ErrorCode(Enum):
    """Enum defining all possible error codes with their status text and HTTP status code.

    Each entry is a tuple of (status_text, http_status_code) representing a distinct error type.

    Common HTTP errors:
        - BAD_REQUEST: HTTP 400 - Invalid request parameters or body
        - NOT_FOUND: HTTP 404 - Resource not found
        - UNAUTHORIZED: HTTP 401 - Authentication required
        - INTERNAL_SERVER_ERROR: HTTP 500 - Server-side error
        - REQUEST_TIMEOUT: HTTP 408 - Request timed out
        - VALIDATION_ERROR: HTTP 422 - Input validation failed
        - FORBIDDEN: HTTP 403 - Insufficient permissions

    Application-specific errors:
        - MAKE_REQUEST_ERROR: HTTP 400 - Error making API request
        - CALL_REQUEST_ERROR: HTTP 400 - Error calling external service
        - READ_BODY_REQUEST_ERROR: HTTP 400 - Error reading request body
        - API_DISABLED: HTTP 403 - API feature is disabled
        - READ_UPLOADED_FILE_ERROR: HTTP 403 - Error reading uploaded file
        - VALIDATION_DATETIME_ERROR: HTTP 422 - Date/time validation error
    """

    # Common HTTP errors
    BAD_REQUEST = ("bad_request", status.HTTP_400_BAD_REQUEST)
    NOT_FOUND = ("not_found", status.HTTP_404_NOT_FOUND)
    UNAUTHORIZED = ("unauthorized", status.HTTP_401_UNAUTHORIZED)
    INTERNAL_SERVER_ERROR = (
        "internal_server_error",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    REQUEST_TIMEOUT = ("request_timeout", status.HTTP_408_REQUEST_TIMEOUT)
    VALIDATION_ERROR = ("validation", status.HTTP_422_UNPROCESSABLE_ENTITY)
    FORBIDDEN = ("not_enough_privileges", status.HTTP_403_FORBIDDEN)

    # Application-specific errors
    MAKE_REQUEST_ERROR = ("make_request_error", status.HTTP_400_BAD_REQUEST)
    CALL_REQUEST_ERROR = ("call_request_error", status.HTTP_400_BAD_REQUEST)
    READ_BODY_REQUEST_ERROR = ("read_body_request_error", status.HTTP_400_BAD_REQUEST)
    API_DISABLED = ("api_disable", status.HTTP_403_FORBIDDEN)
    READ_UPLOADED_FILE_ERROR = ("read_uploaded_file", status.HTTP_403_FORBIDDEN)
    VALIDATION_DATETIME_ERROR = (
        "validation_datetime",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


class AppException(Exception):
    """Base application exception class for centralized error handling."""

    __slots__ = ("status_code", "status_text", "msg", "details")

    def __init__(self, error_code: ErrorCode, msg: str, details: Optional[dict[str, Any]] = None):
        self.status_code = error_code.value[1]
        self.status_text = error_code.value[0]
        self.msg = msg
        self.details = details


# Convenience functions for raising specific exceptions
def bad_request(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.BAD_REQUEST, msg, details)


def not_found(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.NOT_FOUND, msg, details)


def unauthorized(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.UNAUTHORIZED, msg, details)


def internal_server_error(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.INTERNAL_SERVER_ERROR, msg, details)


def request_timeout(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.REQUEST_TIMEOUT, msg, details)


def validation_error(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.VALIDATION_ERROR, msg, details)


def forbidden(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.FORBIDDEN, msg, details)


def make_request_error(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.MAKE_REQUEST_ERROR, msg, details)


def call_request_error(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.CALL_REQUEST_ERROR, msg, details)


def read_body_request_error(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.READ_BODY_REQUEST_ERROR, msg, details)


def api_disabled(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.API_DISABLED, msg, details)


def read_uploaded_file_error(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.READ_UPLOADED_FILE_ERROR, msg, details)


def validation_datetime_error(msg: str, details: Optional[dict[str, Any]] = None) -> AppException:
    return AppException(ErrorCode.VALIDATION_DATETIME_ERROR, msg, details)
