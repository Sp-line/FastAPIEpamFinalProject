"""add User model

Revision ID: 6fbf52d29503
Revises: 3022ede637ee
Create Date: 2026-06-21 20:47:32.766671

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "6fbf52d29503"
down_revision: str | Sequence[str] | None = "3022ede637ee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("project_member_associations",
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("role",
                              sa.Enum(
                                  "OWNER",
                                  "PARTICIPANT",
                                  name="roletype",
                                  native_enum=False,
                                  length=32
                              ),
                              nullable=False
                              ),
                    sa.Column("user_id", sa.Integer(), nullable=False),
                    sa.Column("project_id", sa.Integer(), nullable=False),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
                    sa.ForeignKeyConstraint(
                        ["project_id"],
                        ["projects.id"],
                        name=op.f("fk_project_member_associations_project_id_projects"),
                        ondelete="CASCADE"
                    ),
                    sa.ForeignKeyConstraint(
                        ["user_id"],
                        ["users.id"],
                        name=op.f("fk_project_member_associations_user_id_users"),
                        ondelete="CASCADE"
                    ),
                    sa.PrimaryKeyConstraint("id", name=op.f("pk_project_member_associations")),
                    sa.UniqueConstraint("user_id", "project_id", name="uq_user_project")
                    )
    op.create_index(
        "ix_one_owner_per_project",
        "project_member_associations",
        ["project_id"],
        unique=True,
        postgresql_where=sa.text("role = 'OWNER'")
    )
    op.add_column("projects", sa.Column("creator_id", sa.Integer(), nullable=False))
    op.drop_constraint(op.f("fk_projects_user_id_users"), "projects", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_projects_creator_id_users"),
        "projects",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="CASCADE"
    )
    op.drop_column("projects", "user_id")


def downgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "user_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False)
    )
    op.drop_constraint(
        op.f("fk_projects_creator_id_users"),
        "projects",
        type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_projects_user_id_users"),
        "projects",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )
    op.drop_column("projects", "creator_id")
    op.drop_index(
        "ix_one_owner_per_project",
        table_name="project_member_associations",
        postgresql_where=sa.text("role = 'OWNER'")
    )
    op.drop_table("project_member_associations")
