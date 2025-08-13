from enum import Enum
from typing import Annotated, Any

from fastapi import Depends, Request
from loguru import logger
from pydantic.networks import EmailStr

from app.core.http.api_router import APIRouter
from app.core.messaging.emails import send_test_email
from app.core.ratelimit import limiter
from app.schemas import create_successful_response, Msg, SuccessfulResponse
from app.src.authen.dependencies import get_current_active_authorized
from app.src.users.db_models import User

router = APIRouter()

CurrentUser = Annotated[User, Depends(get_current_active_authorized)]


# Calling this endpoint to see if the setup works.
# If yes, an error message will show in Sentry dashboard
@router.get("/test-sentry")
async def test_sentry(
    *,
    current_user: CurrentUser,
) -> None:  # sourcery skip: raise-specific-error
    """
    Test Sentry.
    """
    1 / 0  # noqa: B018 # NOSONAR


@router.post("/test-email", response_model=SuccessfulResponse[Msg], status_code=201)
async def test_email(
    *,
    email_to: EmailStr,
    current_user: CurrentUser,
) -> Any:
    """
    Test emails.
    """
    await send_test_email(email_to=email_to)
    return create_successful_response(data={"msg": "Test email sent"})


class LoguruLevel(str, Enum):
    info = "info"
    debug = "debug"
    warning = "warning"
    error = "error"
    critical = "critical"


@router.post("/test-loguru", status_code=201)
async def test_loguru(
    *,
    msg: Msg,
    level: LoguruLevel,
    current_user: CurrentUser,
) -> Any:
    """
    Test loguru.
    """

    if level == LoguruLevel.info:
        logger.info(msg.msg)
    elif level == LoguruLevel.debug:
        logger.debug(msg.msg)
    elif level == LoguruLevel.warning:
        logger.warning(msg.msg)
    elif level == LoguruLevel.error:
        logger.error(msg.msg)
    elif level == LoguruLevel.critical:
        logger.critical(msg.msg)


@router.get("/test-ratelimit")
@limiter.limit("2/minute")
@limiter.limit("10/5minute")
async def test_ratelimit(request: Request, current_user: CurrentUser) -> Any:
    """Test rate limit 2 request per minute and 10 request per 5 minute"""
