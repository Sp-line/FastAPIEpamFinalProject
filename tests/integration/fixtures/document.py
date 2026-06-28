from typing import TYPE_CHECKING

import pytest

from app.repositories.document import DocumentRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def integration_document_repo(db_session: AsyncSession) -> DocumentRepository:
    return DocumentRepository(session=db_session)
