from datetime import datetime, timedelta, timezone

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import errors
from app.core.auth.security import create_token, decode_token, verify_password
from app.core.messaging.emails import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)
from app.core.settings import settings
from app.src.service import ServiceBase
from app.src.users import errors as users_errors
from app.src.users.db_models import User
from app.src.users.services import user_service, UserService

from . import errors as authen_errors
from . import schemas
from .cache_repository import authen_cache_repository, AuthenCacheRepository


class AuthenService(ServiceBase):
    def __init__(
        self,
        cache_repository: AuthenCacheRepository,
        user_service: UserService,
    ) -> None:
        self.cache_repository = cache_repository
        self.user_service = user_service

    async def recover_password(self, db: AsyncSession, email: str) -> None:
        user = await self.user_service.get_by_email(db, cache_connection=None, email=email)

        if not user:
            raise errors.not_found(msg="User not exists")

        password_reset_token = generate_password_reset_token(email=email)

        await send_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )

    async def reset_password(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        token: str,
        new_password: str,
    ) -> None:
        email = verify_password_reset_token(token)
        if not email:
            raise authen_errors.invalid_reset_password_token(msg="Invalid reset password token")

        user = await self.user_service.get_by_email(
            db, cache_connection=cache_connection, email=email
        )
        if not user:
            raise users_errors.user_not_found()
        if not user.is_active:
            raise authen_errors.inactive_user(msg="User inactive")

        await self.user_service.update_password(
            db,
            cache_connection=cache_connection,
            db_obj=user,
            new_password=new_password,
        )

    def parse_token(self, token: str, secret_key: str) -> schemas.TokenPayload:
        try:
            payload = decode_token(token, secret_key)
            token_data = schemas.TokenPayload(**payload)
        except ExpiredSignatureError as e:
            raise authen_errors.expired_jwt_token("token is expired") from e
        except (InvalidTokenError, ValidationError) as e:
            raise authen_errors.invalid_jwt_token("could not validate credentials") from e

        if token_data.sub is None:
            raise authen_errors.invalid_jwt_token("could not validate credentials")

        return token_data

    async def create_token(self, user: User) -> tuple[str, str, datetime, datetime]:
        access_token_expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.TOKEN.ACCESS_TOKEN_EXPIRE_DURATION
        )
        refresh_token_expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.TOKEN.REFRESH_TOKEN_EXPIRE_DURATION
        )

        access_token = create_token(
            user.email,
            secret_key=settings.TOKEN.ACCESS_TOKEN_SECRET_KEY,
            expire=access_token_expire,
        )
        refresh_token = create_token(
            user.email,
            secret_key=settings.TOKEN.REFRESH_TOKEN_SECRET_KEY,
            expire=refresh_token_expire,
        )

        return access_token, refresh_token, access_token_expire, refresh_token_expire

    async def login(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        email: str,
        password: str,
    ) -> tuple[str, str, datetime, datetime]:
        user = await self.user_service.get_by_email(
            db, cache_connection=cache_connection, email=email
        )
        if not user:
            raise users_errors.user_not_found()

        if user.hashed_password is None or not verify_password(password, user.hashed_password):
            raise authen_errors.wrong_password("Incorrect email or password")

        if not user.is_active:
            raise authen_errors.inactive_user("inactive user")

        (
            access_token,
            refresh_token,
            access_token_expire,
            refresh_token_expire,
        ) = await self.create_token(user=user)

        await self.cache_repository.add_refresh_token(
            connection=cache_connection,
            obj_email=user.email,
            refresh_token=refresh_token,
            expire=refresh_token_expire,
        )

        return access_token, refresh_token, access_token_expire, refresh_token_expire

    async def get_user_from_token(
        self, db: AsyncSession, cache_connection: Redis, token: str
    ) -> User | None:
        token_data = self.parse_token(
            token=token, secret_key=settings.TOKEN.ACCESS_TOKEN_SECRET_KEY
        )

        return await self.user_service.get_by_email(
            db, cache_connection=cache_connection, email=str(token_data.sub)
        )

    async def exchange_oidc_token(
        self,
        cache_connection: Redis,
        user: User,
    ) -> tuple[str, str, datetime, datetime]:
        (
            access_token,
            refresh_token,
            access_token_expire,
            refresh_token_expire,
        ) = await self.create_token(user=user)

        await self.cache_repository.add_refresh_token(
            connection=cache_connection,
            obj_email=user.email,
            refresh_token=refresh_token,
            expire=refresh_token_expire,
        )

        return access_token, refresh_token, access_token_expire, refresh_token_expire

    async def refresh_token(
        self,
        db: AsyncSession,
        cache_connection: Redis,
        old_refresh_token: str,
    ) -> tuple[str, str, datetime, datetime]:
        token_data = self.parse_token(
            token=old_refresh_token, secret_key=settings.TOKEN.REFRESH_TOKEN_SECRET_KEY
        )

        if not await self.cache_repository.check_refresh_token(
            connection=cache_connection,
            obj_email=token_data.sub,
            refresh_token=old_refresh_token,
        ):
            raise authen_errors.refresh_token_not_found("not found refresh token in redis")

        await self.cache_repository.delete_refresh_token(
            connection=cache_connection,
            obj_email=token_data.sub,
            refresh_token=old_refresh_token,
        )

        user = await self.user_service.get_by_email(
            db, cache_connection=cache_connection, email=str(token_data.sub)
        )
        if not user:
            raise users_errors.user_not_found()

        (
            access_token,
            refresh_token,
            access_token_expire,
            refresh_token_expire,
        ) = await self.create_token(user=user)

        await self.cache_repository.add_refresh_token(
            connection=cache_connection,
            obj_email=token_data.sub,
            refresh_token=refresh_token,
            expire=refresh_token_expire,
        )

        return access_token, refresh_token, access_token_expire, refresh_token_expire

    async def logout(self, cache_connection: Redis, refresh_token: str) -> None:
        token_data = self.parse_token(
            token=refresh_token, secret_key=settings.TOKEN.REFRESH_TOKEN_SECRET_KEY
        )

        await self.cache_repository.delete_refresh_token(
            connection=cache_connection,
            obj_email=token_data.sub,
            refresh_token=refresh_token,
        )

    async def logout_all(self, cache_connection: Redis, email: str) -> None:
        await self.cache_repository.delete_all_refresh_token(
            connection=cache_connection,
            obj_email=email,
        )

    async def logout_all_with_token(self, cache_connection: Redis, refresh_token: str) -> None:
        token_data = self.parse_token(
            token=refresh_token, secret_key=settings.TOKEN.REFRESH_TOKEN_SECRET_KEY
        )

        await self.cache_repository.delete_all_refresh_token(
            connection=cache_connection,
            obj_email=token_data.sub,
        )


authen_service = AuthenService(
    cache_repository=authen_cache_repository,
    user_service=user_service,
)
