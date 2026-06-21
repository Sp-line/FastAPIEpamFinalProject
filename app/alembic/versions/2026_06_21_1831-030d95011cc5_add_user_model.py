"""add User model

Revision ID: 030d95011cc5
Revises:
Create Date: 2026-06-21 18:31:34.644153

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "030d95011cc5"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("users",
                    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("username", sa.String(length=32), nullable=False),
    sa.Column("hashed_password", sa.String(length=1024), nullable=False),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    sa.UniqueConstraint("username", name=op.f("uq_users_username"))
    )


def downgrade() -> None:
    op.drop_table("users")
