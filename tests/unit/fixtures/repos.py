from unittest.mock import AsyncMock

import pytest

from app.repositories.document import DocumentRepository
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberAssociationRepository
from app.repositories.unit_of_work import UnitOfWork
from app.repositories.user import UserRepository


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_project_repo() -> AsyncMock:
    return AsyncMock(spec=ProjectRepository)


@pytest.fixture
def mock_project_member_repo() -> AsyncMock:
    return AsyncMock(spec=ProjectMemberAssociationRepository)


@pytest.fixture
def mock_document_repo() -> AsyncMock:
    return AsyncMock(spec=DocumentRepository)


@pytest.fixture
def real_user_repo(mock_session: AsyncMock) -> UserRepository:
    return UserRepository(session=mock_session)


@pytest.fixture
def real_uow(mock_session: AsyncMock) -> UnitOfWork:
    return UnitOfWork(session=mock_session)


@pytest.fixture
def real_project_repo(mock_session: AsyncMock) -> ProjectRepository:
    return ProjectRepository(session=mock_session)
