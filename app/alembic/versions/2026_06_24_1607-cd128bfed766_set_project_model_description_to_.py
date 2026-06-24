"""set Project model description to nullable

Revision ID: cd128bfed766
Revises: f2698bdb56cc
Create Date: 2026-06-24 16:07:16.971481

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cd128bfed766"
down_revision: str | Sequence[str] | None = "f2698bdb56cc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("projects", "description",
               existing_type=sa.TEXT(),
               nullable=True)


def downgrade() -> None:
    op.alter_column("projects", "description",
               existing_type=sa.TEXT(),
               nullable=False)
