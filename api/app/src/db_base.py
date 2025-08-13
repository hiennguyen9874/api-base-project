from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import TypeDecorator
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from app.core.settings import settings

constraint_naming_conventions = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> Any:
        if value is not None and not value.tzinfo:
            raise TypeError("tzinfo is required")
        return value.astimezone(timezone.utc) if value is not None else None

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> Any:
        if value is not None:
            value = value.astimezone(ZoneInfo(settings.APP.TIMEZONE))
        return value


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime(timezone=True), default=func.now(), nullable=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TZDateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class Base(DeclarativeBase):
    # metadata = MetaData(naming_convention=constraint_naming_conventions)  # type: ignore

    id: Any

    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa B904 pylint: disable=no-self-argument
        # sourcery skip: instance-method-first-arg-name
        return cls.__name__.lower()

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}
