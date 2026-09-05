from datetime import datetime
from typing import Any, Sequence, Type

from dateutil import tz
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.security import get_password_hash
from app.core.messaging.emails import send_new_account_email
from app.core.settings import settings

from .db_models import User
from .db_repository import user_db_repository, UserDbRepository
from .schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, model: Type[User], db_repository: UserDbRepository) -> None:
        self.model = model
        self.db_repository = db_repository

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        db_obj = self.model(  # type: ignore
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            avatar_url=obj_in.avatar_url,
            default_currency=obj_in.default_currency,
            language_preference=obj_in.language_preference,
            registration_date=datetime.now(tz.tzlocal()),
            is_active=True,
            account_status="ACTIVE",
        )
        return await self.db_repository.create(db=db, db_obj=db_obj)

    async def create_user(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        user = await self.create(db, obj_in=obj_in)

        if settings.EMAIL.ENABLED and obj_in.email:
            await send_new_account_email(
                email_to=obj_in.email,
                username=obj_in.email,
                password=obj_in.password,
            )

        return user

    async def get_or_create_by_email(
        self,
        db: AsyncSession,
        email: str,
        **kwargs: Any | None,
    ) -> tuple[User, bool]:
        return await self.db_repository.get_or_create_by_email(db=db, email=email, **kwargs)

    async def get_all(self, db: AsyncSession) -> Sequence[User]:
        return await self.db_repository.get_all(db=db)

    async def get_multi(
        self, db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> Sequence[User]:
        return await self.db_repository.get_multi(db=db, offset=offset, limit=limit)

    async def get_multi_count(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[User], int]:
        users = await self.get_multi(db=db, offset=offset, limit=limit)
        total = await self.db_repository.count_all(db=db)
        return users, total

    async def get(
        self,
        db: AsyncSession,
        id: int,  # pylint: disable=redefined-builtin
    ) -> User | None:
        return await self.db_repository.get(db=db, id=id)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        return await self.db_repository.get_by_email(db=db, email=email)

    async def delete(self, db: AsyncSession, db_obj: User) -> None:
        await self.db_repository.delete(db=db, db_obj=db_obj)

    async def update(
        self,
        db: AsyncSession,
        db_obj: User,
        obj_in: UserUpdate | dict[str, Any],
    ) -> User:
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data=(obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)),
        )

    async def update_user_me(
        self,
        db: AsyncSession,
        db_obj: User,
        full_name: str | None = None,
        avatar_url: str | None = None,
        default_currency: str | None = None,
        language_preference: str | None = None,
    ) -> User:
        user_in = UserUpdate()
        if full_name is not None:
            user_in.full_name = full_name
        if avatar_url is not None:
            user_in.avatar_url = avatar_url
        if default_currency is not None:
            user_in.default_currency = default_currency
        if language_preference is not None:
            user_in.language_preference = language_preference
        return await self.update(db, db_obj=db_obj, obj_in=user_in)

    async def update_password(
        self,
        db: AsyncSession,
        db_obj: User,
        new_password: str,
    ) -> User:
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data={"hashed_password": get_password_hash(new_password)},
        )

    async def update_last_login(self, db: AsyncSession, db_obj: User) -> User:
        """Update the last_login_date of a user to current time."""
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data={"last_login_date": datetime.now(tz.tzlocal())},
        )

    async def update_account_status(
        self,
        db: AsyncSession,
        db_obj: User,
        status: str,
    ) -> User:
        """Update the account status of a user."""
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data={"account_status": status},
        )

    async def enable_two_factor(
        self,
        db: AsyncSession,
        db_obj: User,
        secret: str,
    ) -> User:
        """Enable two-factor authentication for a user."""
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data={"two_factor_enabled": True, "two_factor_secret": secret},
        )

    async def disable_two_factor(self, db: AsyncSession, db_obj: User) -> User:
        """Disable two-factor authentication for a user."""
        return await self.db_repository.update(
            db=db,
            db_obj=db_obj,
            update_data={"two_factor_enabled": False, "two_factor_secret": None},
        )


user_service = UserService(model=User, db_repository=user_db_repository)
