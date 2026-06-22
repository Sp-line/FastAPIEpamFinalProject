"""add Project model

Revision ID: b903a6219ef2
Revises: df2b9e27b23f
Create Date: 2026-06-21 19:34:08.418095

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b903a6219ef2"
down_revision: str | Sequence[str] | None = "df2b9e27b23f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("projects",
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("name", sa.String(length=64), nullable=False),
                    sa.Column("description", sa.Text(), nullable=False),
                    sa.Column("user_id", sa.Integer(), nullable=False),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
                    sa.ForeignKeyConstraint(
                        ["user_id"],
                        ["users.id"],
                        name=op.f("fk_projects_user_id_users"), ondelete="CASCADE"
                    ),
                    sa.PrimaryKeyConstraint("id", name=op.f("pk_projects"))
                    )


def downgrade() -> None:
    op.drop_table("projects")
