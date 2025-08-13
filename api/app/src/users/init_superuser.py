import casbin
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.src import db_models  # type: ignore # noqa: F401
from app.src.author.services import casbin_service

from .schemas import UserCreate
from .services import user_service

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_superuser(
    db: AsyncSession,
    enforcer: casbin.AsyncEnforcer,
) -> bool:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = await user_service.get_by_email(
        db,
        cache_connection=None,
        email=settings.USER.FIRST_USER_EMAIL,
    )

    if user:
        return False

    user_in = UserCreate(
        email=settings.USER.FIRST_USER_EMAIL,
        password=settings.USER.FIRST_USER_PASSWORD,
        full_name=settings.USER.FIRST_USER_FULL_NAME,
    )
    await user_service.create_user(db, obj_in=user_in, enforcer=enforcer)  # noqa: F841
    await casbin_service.add_role_for_user(
        db=db,
        enforcer=enforcer,
        email=settings.USER.FIRST_USER_EMAIL,
        role=settings.USER.FIRST_USER_ROLE,
    )
    return True
