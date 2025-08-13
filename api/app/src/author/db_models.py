from typing import Any

from sqlalchemy import Index, String
from sqlalchemy.orm import declared_attr, Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from app.src.db_base import Base, TimestampMixin

__all__ = ["CasbinRule"]


class CasbinRule(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ptype: Mapped[str | None] = mapped_column(index=True)
    v0: Mapped[str | None] = mapped_column(String(255))
    v1: Mapped[str | None] = mapped_column(String(255))
    v2: Mapped[str | None] = mapped_column(String(255))
    v3: Mapped[str | None] = mapped_column(String(255))
    v4: Mapped[str | None] = mapped_column(String(255))
    v5: Mapped[str | None] = mapped_column(String(255))

    def __str__(self) -> str:
        return ", ".join(
            v
            for v in (self.ptype, self.v0, self.v1, self.v2, self.v3, self.v4, self.v5)
            if v is not None
        )

    def __repr__(self) -> str:
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))

    @declared_attr.directive
    def __table_args__(cls) -> Any:
        return (
            Index("ix_casbin_rule_all", "ptype", "v0", "v1", "v2", "v3", "v4", "v5"),
            UniqueConstraint(
                "ptype",
                "v0",
                "v1",
                "v2",
                "v3",
                "v4",
                "v5",
                postgresql_nulls_not_distinct=True,
            ),
        )
