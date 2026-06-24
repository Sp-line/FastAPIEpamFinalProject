from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.models.base import Base
from app.core.models.mixins.int_id_pk import IntIdPkMixin


class DummyModel(IntIdPkMixin, Base):
    __tablename__ = "dummy_models"

    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(100), nullable=True)


class DummyCreate(BaseModel):
    name: str
    description: str | None = None


class DummyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
