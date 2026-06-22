"""add Check Constraints for Project model

Revision ID: f2698bdb56cc
Revises: 4befb046a318
Create Date: 2026-06-22 13:49:12.109406

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from alembic import op

revision: str = "f2698bdb56cc"
down_revision: str | Sequence[str] | None = "4befb046a318"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_project_name_min_len",
        "projects",
        "char_length(name) >= 2"
    )


def downgrade() -> None:
    op.drop_constraint("check_project_name_min_len", "projects", type_="check")
