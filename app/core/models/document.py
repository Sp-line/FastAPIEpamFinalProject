from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants import DocumentLimits
from app.core.models.base import Base
from app.core.models.mixins import IntIdPkMixin
from app.core.models.mixins import ObservableMixin

if TYPE_CHECKING:
    from app.core.models.project import Project


class Document(IntIdPkMixin, ObservableMixin, Base):
    original_name: Mapped[str] = mapped_column(String(DocumentLimits.ORIGINAL_NAME_MAX))
    s3_key: Mapped[str] = mapped_column(String(DocumentLimits.S3_KEY_MAX), unique=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )

    project: Mapped[Project] = relationship(back_populates="documents")
