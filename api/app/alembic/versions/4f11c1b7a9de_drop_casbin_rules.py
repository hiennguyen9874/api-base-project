"""drop casbin rules

Revision ID: 4f11c1b7a9de
Revises: ee54ca148397
Create Date: 2026-09-05

"""

from alembic import op
import sqlalchemy as sa


revision = "4f11c1b7a9de"
down_revision = "ee54ca148397"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("casbinrule")


def downgrade():
    op.create_table(
        "casbinrule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ptype", sa.String(), nullable=True),
        sa.Column("v0", sa.String(length=255), nullable=True),
        sa.Column("v1", sa.String(length=255), nullable=True),
        sa.Column("v2", sa.String(length=255), nullable=True),
        sa.Column("v3", sa.String(length=255), nullable=True),
        sa.Column("v4", sa.String(length=255), nullable=True),
        sa.Column("v5", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ptype", "v0", "v1", "v2", "v3", "v4", "v5", postgresql_nulls_not_distinct=True
        ),
    )
    op.create_index(
        "ix_casbin_rule_all",
        "casbinrule",
        ["ptype", "v0", "v1", "v2", "v3", "v4", "v5"],
        unique=False,
    )
    op.create_index(op.f("ix_casbinrule_id"), "casbinrule", ["id"], unique=False)
    op.create_index(op.f("ix_casbinrule_ptype"), "casbinrule", ["ptype"], unique=False)
