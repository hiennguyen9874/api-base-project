from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.src import db_models  # type: ignore # noqa: F401

from .schemas import UserCreate
from .services import user_service

# Make sure all SQLAlchemy models are imported before initializing the database.


async def init_superuser(db: AsyncSession) -> bool:
    user = await user_service.get_by_email(db, email=settings.USER.FIRST_USER_EMAIL)
    if user:
        return False

    user_in = UserCreate(
        email=settings.USER.FIRST_USER_EMAIL,
        password=settings.USER.FIRST_USER_PASSWORD,
        full_name=settings.USER.FIRST_USER_FULL_NAME,
    )
    await user_service.create_user(db, obj_in=user_in)
    return True
