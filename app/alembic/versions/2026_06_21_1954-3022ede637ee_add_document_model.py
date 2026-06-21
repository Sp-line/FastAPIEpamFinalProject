"""add Document model

Revision ID: 3022ede637ee
Revises: b903a6219ef2
Create Date: 2026-06-21 19:54:57.840394

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3022ede637ee"
down_revision: str | Sequence[str] | None = "b903a6219ef2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("documents",
                    sa.Column(
                        "original_name",
                        sa.String(length=255),
                        nullable=False
                    ),
                    sa.Column("s3_key", sa.String(length=1024), nullable=False),
                    sa.Column("project_id", sa.Integer(), nullable=False),
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column(
                        "created_at",
                        sa.DateTime(),
                        server_default=sa.text("now()"),
                        nullable=False
                    ),
                    sa.Column(
                        "updated_at",
                        sa.DateTime(),
                        server_default=sa.text("now()"),
                        nullable=False
                    ),
                    sa.ForeignKeyConstraint(
                        ["project_id"],
                        ["projects.id"],
                        name=op.f("fk_documents_project_id_projects"), ondelete="CASCADE"
                    ),
                    sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
                    sa.UniqueConstraint("s3_key", name=op.f("uq_documents_s3_key"))
                    )


def downgrade() -> None:
    op.drop_table("documents")
