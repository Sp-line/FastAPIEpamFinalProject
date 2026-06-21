from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants.user import UserLimits
from app.core.models.base import Base
from app.core.models.mixins import ObservableMixin
from app.core.models.mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from app.core.models.project import Project


class User(IntIdPkMixin, ObservableMixin, Base):
    username: Mapped[str] = mapped_column(String(UserLimits.USERNAME_MAX), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(UserLimits.HASHED_PASSWORD_MAX))

    projects: Mapped[list[Project]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
