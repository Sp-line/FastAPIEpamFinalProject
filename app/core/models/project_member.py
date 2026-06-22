from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants.project_member import ProjectMemberLimits
from app.constants.role_type import RoleType
from app.core.models.base import Base
from app.core.models.mixins.int_id_pk import IntIdPkMixin
from app.core.models.mixins.observable import ObservableMixin

if TYPE_CHECKING:
    from app.core.models.project import Project
    from app.core.models.user import User


class ProjectMemberAssociation(IntIdPkMixin, ObservableMixin, Base):
    role: Mapped[RoleType] = mapped_column(
        SAEnum(
            RoleType,
            native_enum=False,
            length=ProjectMemberLimits.ROLE_TYPE_MAX,
        ),
        default=RoleType.PARTICIPANT,
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )

    user: Mapped[User] = relationship(back_populates="project_associations")
    project: Mapped[Project] = relationship(back_populates="user_associations")

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_user_project"),
        Index(
            "ix_one_owner_per_project",
            "project_id",
            unique=True,
            postgresql_where=(role == RoleType.OWNER),
        ),
    )
