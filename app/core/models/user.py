from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants.user import UserLimits
from app.core.models.base import Base
from app.core.models.mixins.int_id_pk import IntIdPkMixin
from app.core.models.mixins.observable import ObservableMixin

if TYPE_CHECKING:
    from app.core.models.project import Project
    from app.core.models.project_member import ProjectMemberAssociation


class User(IntIdPkMixin, ObservableMixin, Base):
    username: Mapped[str] = mapped_column(String(UserLimits.USERNAME_MAX), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(UserLimits.HASHED_PASSWORD_MAX))

    created_projects: Mapped[list[Project]] = relationship(
        back_populates="creator", cascade="all, delete-orphan"
    )

    project_associations: Mapped[list[ProjectMemberAssociation]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    projects: Mapped[list[Project]] = relationship(
        secondary="project_member_associations",
        back_populates="users",
        viewonly=True,
        overlaps="project_associations",
    )

    __table_args__ = (
        CheckConstraint(
            func.char_length(username) >= UserLimits.USERNAME_MIN,
            name="check_user_username_min_len",
        ),
        CheckConstraint(
            func.char_length(hashed_password) >= UserLimits.HASHED_PASSWORD_MIN,
            name="check_user_hashed_password_min_len",
        ),
    )
