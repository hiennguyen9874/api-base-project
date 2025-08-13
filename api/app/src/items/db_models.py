from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.src.db_base import Base

if TYPE_CHECKING:
    from app.src.users.db_models import User  # noqa: F401


__all__ = ["Item"]


class Item(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str | None] = mapped_column(index=True)
    description: Mapped[str | None] = mapped_column(index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    owner: Mapped[User] = relationship(back_populates="items", lazy="select")
