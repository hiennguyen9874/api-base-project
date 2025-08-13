from typing import Any

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.src.db_repository import BaseDbRepository

from .db_models import User


class UserDbRepository(BaseDbRepository[User]):
    async def get_or_create_by_email(
        self, db: AsyncSession, email: str, **kwargs: Any | None
    ) -> tuple[User, bool]:
        user = (
            (await db.execute(select(self.model).where(self.model.email == email)))
            .scalars()
            .one_or_none()
        )
        if user:
            # exist
            return user, False

        try:
            user = self.model(email=email, **kwargs)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user, True
        except exc.IntegrityError:
            await db.rollback()
            user = (
                (await db.execute(select(self.model).where(self.model.email == email)))
                .scalars()
                .one()
            )
            return user, False

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        q = await db.execute(select(self.model).where(self.model.email == email))
        return q.scalars().one_or_none()


user_db_repository = UserDbRepository(model=User)
