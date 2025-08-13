from typing import Any

from app.core.http.api_router import APIRouter
from app.schemas import ErrorResponse, ValidationErrorResponse

from .authen.router import router as authen_router
from .author.router import router as author_router
from .items.router import router as items_router
from .tests.router import router as tests_router
from .users.router import router as users_router

common_responses: dict[int | str, dict[str, Any]] | None = {
    400: {
        "model": ErrorResponse[list[dict[str, Any]] | dict[str, Any] | str],
        "description": "Could not validate credentials",
    },
    403: {
        "model": ErrorResponse[list[dict[str, Any]] | dict[str, Any] | str],
        "description": "Inactive user or The user doesn't have enough privileges",
    },
    404: {
        "model": ErrorResponse[list[dict[str, Any]] | dict[str, Any] | str],
        "description": "User not found",
    },
}

api_router = APIRouter(
    responses={
        422: {
            "model": ValidationErrorResponse[list[dict[str, Any]] | dict[str, Any] | str],
            "description": "Validation Error",
        }
    }
)

api_router.include_router(users_router, responses=common_responses)  # type: ignore[arg-type]
api_router.include_router(authen_router, responses=common_responses)  # type: ignore[arg-type]
api_router.include_router(author_router, responses=common_responses)  # type: ignore[arg-type]
api_router.include_router(items_router, responses=common_responses)  # type: ignore[arg-type]
api_router.include_router(tests_router, responses=common_responses)
