"""add ObservableMixin for User model

Revision ID: df2b9e27b23f
Revises: 030d95011cc5
Create Date: 2026-06-21 19:01:15.856093

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "df2b9e27b23f"
down_revision: str | Sequence[str] | None = "030d95011cc5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users",
                  sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False)
                  )
    op.add_column("users",
                  sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False)
                  )


def downgrade() -> None:
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
