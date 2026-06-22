from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants.project import ProjectLimits
from app.core.models.base import Base
from app.core.models.mixins.int_id_pk import IntIdPkMixin
from app.core.models.mixins.observable import ObservableMixin

if TYPE_CHECKING:
    from app.core.models.document import Document
    from app.core.models.project_member import ProjectMemberAssociation
    from app.core.models.user import User


class Project(IntIdPkMixin, ObservableMixin, Base):
    name: Mapped[str] = mapped_column(String(ProjectLimits.NAME_MAX))
    description: Mapped[str] = mapped_column(Text)

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    creator: Mapped[User] = relationship(back_populates="created_projects")

    users: Mapped[list[User]] = relationship(
        secondary="project_member_associations",
        back_populates="projects",
        viewonly=True,
        overlaps="user_associations",
    )
    documents: Mapped[list[Document]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    user_associations: Mapped[list[ProjectMemberAssociation]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            func.char_length(name) >= ProjectLimits.NAME_MIN,
            name="check_project_name_min_len",
        ),
    )
