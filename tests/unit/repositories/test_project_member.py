from unittest.mock import MagicMock

import pytest

from app.core.models.project_member import ProjectMemberAssociation
from app.repositories.project_member import ProjectMemberAssociationRepository


@pytest.fixture
def repo(mock_session: MagicMock) -> ProjectMemberAssociationRepository:
    return ProjectMemberAssociationRepository(session=mock_session)


async def test_get_by_user_and_project_executes_query_and_returns_model(
    repo: ProjectMemberAssociationRepository,
    mock_session: MagicMock,
) -> None:
    mock_result = MagicMock()
    expected_model = ProjectMemberAssociation(id=1, user_id=42, project_id=10)
    mock_result.scalar_one_or_none.return_value = expected_model
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_user_and_project(user_id=42, project_id=10)

    mock_session.execute.assert_awaited_once()
    mock_result.scalar_one_or_none.assert_called_once()
    assert result == expected_model


async def test_get_by_user_and_project_returns_none_if_no_record(
    repo: ProjectMemberAssociationRepository,
    mock_session: MagicMock,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_user_and_project(user_id=99, project_id=99)

    mock_session.execute.assert_awaited_once()
    mock_result.scalar_one_or_none.assert_called_once()
    assert result is None
