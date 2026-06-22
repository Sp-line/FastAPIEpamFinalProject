"""add Check Constraints for Document model

Revision ID: 80e3f11914c5
Revises: 6fbf52d29503
Create Date: 2026-06-22 13:19:01.211306

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from alembic import op

revision: str = "80e3f11914c5"
down_revision: str | Sequence[str] | None = "6fbf52d29503"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_document_original_name_min_len",
        "documents",
        "char_length(original_name) >= 1"
    )
    op.create_check_constraint(
        "check_document_s3_key_min_len",
        "documents",
        "char_length(s3_key) >= 36"
    )


def downgrade() -> None:
    op.drop_constraint("check_document_s3_key_min_len", "documents", type_="check")
    op.drop_constraint("check_document_original_name_min_len", "documents", type_="check")
