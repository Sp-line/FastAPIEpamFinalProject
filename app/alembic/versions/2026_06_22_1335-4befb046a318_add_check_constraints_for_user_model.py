"""add Check Constraints for User model

Revision ID: 4befb046a318
Revises: 80e3f11914c5
Create Date: 2026-06-22 13:35:37.291449

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from alembic import op

revision: str = "4befb046a318"
down_revision: str | Sequence[str] | None = "80e3f11914c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_user_username_min_len",
        "users",
        "char_length(username) >= 2"
    )
    op.create_check_constraint(
        "check_user_hashed_password_min_len",
        "users",
        "char_length(hashed_password) >= 50"
    )


def downgrade() -> None:
    op.drop_constraint("check_user_hashed_password_min_len", "users", type_="check")
    op.drop_constraint("check_user_username_min_len", "users", type_="check")
