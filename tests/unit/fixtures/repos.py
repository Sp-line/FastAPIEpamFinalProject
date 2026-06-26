from unittest.mock import AsyncMock

import pytest

from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberAssociationRepository
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
