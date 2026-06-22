from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.constants.document import DocumentLimits
from app.core.models.base import Base
from app.core.models.mixins.int_id_pk import IntIdPkMixin
from app.core.models.mixins.observable import ObservableMixin

if TYPE_CHECKING:
    from app.core.models.project import Project


class Document(IntIdPkMixin, ObservableMixin, Base):
    original_name: Mapped[str] = mapped_column(String(DocumentLimits.ORIGINAL_NAME_MAX))
    s3_key: Mapped[str] = mapped_column(String(DocumentLimits.S3_KEY_MAX), unique=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )

    project: Mapped[Project] = relationship(back_populates="documents")

    __table_args__ = (
        CheckConstraint(
            func.char_length(original_name) >= DocumentLimits.ORIGINAL_NAME_MIN,
            name="check_document_original_name_min_len",
        ),
        CheckConstraint(
            func.char_length(s3_key) >= DocumentLimits.S3_KEY_MIN,
            name="check_document_s3_key_min_len",
        ),
    )
