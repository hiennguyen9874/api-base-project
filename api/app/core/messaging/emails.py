from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jwt.exceptions import InvalidTokenError
from loguru import logger

from app.core.settings import settings

__all__ = [
    "send_email",
    "send_test_email",
    "send_reset_password_email",
    "send_new_account_email",
    "generate_password_reset_token",
    "verify_password_reset_token",
]

conf = (
    ConnectionConfig(
        MAIL_USERNAME=settings.EMAIL.SMTP_USER,
        MAIL_PASSWORD=settings.EMAIL.SMTP_PASSWORD,
        MAIL_PORT=settings.EMAIL.SMTP_PORT,
        MAIL_SERVER=settings.EMAIL.SMTP_HOST,
        MAIL_SSL_TLS=settings.EMAIL.SMTP_TLS,
        MAIL_FROM=settings.EMAIL.FROM_EMAIL,
        MAIL_FROM_NAME=settings.EMAIL.FROM_NAME,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=settings.EMAIL.TEMPLATES_DIR,
    )
    if (
        settings.EMAIL.SMTP_USER is not None
        and settings.EMAIL.SMTP_PASSWORD is not None
        and settings.EMAIL.SMTP_PORT is not None
        and settings.EMAIL.SMTP_HOST is not None
        and settings.EMAIL.SMTP_TLS is not None
        and settings.EMAIL.FROM_EMAIL is not None
        and settings.EMAIL.FROM_NAME is not None
        and settings.EMAIL.TEMPLATES_DIR is not None
    )
    else None
)


async def send_email(
    email_to: str,
    subject: str = "",
    template_name: str = "",
    environment: dict[str, Any] | None = None,  # noqa: B006
) -> bool:
    assert settings.EMAIL.ENABLED, "no provided configuration for email variables"
    if conf is None:
        return False

    if environment is None:
        environment = {}

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=environment,
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(message, template_name=template_name)

    logger.info("send email result")

    return True


async def send_test_email(email_to: str) -> None:
    project_name = settings.EMAIL.PROJECT_NAME

    subject = f"{project_name} - Test email"

    await send_email(
        email_to=email_to,
        subject=subject,
        template_name="test_email.html",
        environment={"project_name": settings.EMAIL.PROJECT_NAME, "email": email_to},
    )


async def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.EMAIL.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    server_host = settings.EMAIL.SERVER_HOST

    link = f"{server_host}/reset-password?token={token}"

    await send_email(
        email_to=email_to,
        subject=subject,
        template_name="reset_password.html",
        environment={
            "project_name": settings.EMAIL.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL.RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


async def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.EMAIL.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"

    link = settings.EMAIL.SERVER_HOST

    await send_email(
        email_to=email_to,
        subject=subject,
        template_name="new_account.html",
        environment={
            "project_name": settings.EMAIL.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(minutes=settings.EMAIL.RESET_TOKEN_EXPIRE_DURATION)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    return jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.EMAIL.RESET_TOKEN_SECRET_KEY,
        algorithm=settings.EMAIL.RESET_TOKEN_ALGORITHM,
    )


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.EMAIL.RESET_TOKEN_SECRET_KEY,
            algorithms=[settings.EMAIL.RESET_TOKEN_ALGORITHM],
        )
        return decoded_token["sub"]
    except InvalidTokenError:
        return None
