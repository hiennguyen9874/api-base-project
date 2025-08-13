from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.src.db_base import Base, TimestampMixin, TZDateTime

if TYPE_CHECKING:
    from app.src.items.db_models import Item  # noqa: F401

__all__ = ["User"]


class User(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    full_name: Mapped[str | None] = mapped_column(index=False, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    default_currency: Mapped[str] = mapped_column(String(3), default="VND", nullable=False)
    language_preference: Mapped[str] = mapped_column(String(5), default="vi-VN", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String, nullable=True)
    registration_date: Mapped[datetime] = mapped_column(
        TZDateTime(timezone=True), default=func.now(), nullable=False
    )
    last_login_date: Mapped[datetime | None] = mapped_column(
        TZDateTime(timezone=True), nullable=True
    )
    account_status: Mapped[str] = mapped_column(String, default="ACTIVE", nullable=False)

    items: Mapped[list[Item]] = relationship(back_populates="owner", lazy="select")
