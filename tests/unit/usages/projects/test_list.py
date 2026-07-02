from typing import TYPE_CHECKING

import pytest

from app.schemas.project import ProjectInfoReadWithDocuments
from tests.factories.project import ProjectInfoReadWithDocumentsFactory

if TYPE_CHECKING:
    from unittest.mock import AsyncMock
    from unittest.mock import MagicMock

    from app.usages.projects.list import ProjectListInfoUsage


async def test_project_list_info_usage_returns_projects_when_allowed_ids_exist(
    project_list_info_usage: ProjectListInfoUsage,
    mock_project_member_repo: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_ensure_can_retrieve_project: MagicMock,
    mock_uow: AsyncMock,
) -> None:
    current_user_id = 42
    allowed_project_ids = [1, 2, 3]

    mock_project_member_repo.get_project_ids_by_user_and_roles.return_value = (
        allowed_project_ids
    )

    db_projects = [
        ProjectInfoReadWithDocumentsFactory.build(id=1).model_dump(),
        ProjectInfoReadWithDocumentsFactory.build(id=2).model_dump(),
        ProjectInfoReadWithDocumentsFactory.build(id=3).model_dump(),
    ]
    mock_project_repo.get_by_ids_with_documents.return_value = db_projects

    results = await project_list_info_usage(current_user_id=current_user_id)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_project_member_repo.get_project_ids_by_user_and_roles.assert_awaited_once_with(
        user_id=current_user_id,
        roles=mock_ensure_can_retrieve_project.allowed_roles,
    )

    mock_project_repo.get_by_ids_with_documents.assert_awaited_once_with(
        allowed_project_ids
    )

    assert isinstance(results, list)
    assert len(results) == 3  # noqa: PLR2004
    assert all(isinstance(proj, ProjectInfoReadWithDocuments) for proj in results)
    assert [proj.id for proj in results] == [1, 2, 3]


async def test_project_list_info_usage_returns_empty_list_when_no_allowed_ids(
    project_list_info_usage: ProjectListInfoUsage,
    mock_project_member_repo: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    current_user_id = 99

    mock_project_member_repo.get_project_ids_by_user_and_roles.return_value = []

    results = await project_list_info_usage(current_user_id=current_user_id)

    assert results == []

    mock_project_repo.get_by_ids_with_documents.assert_not_called()

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()


async def test_project_list_info_usage_bubbles_up_db_exceptions(
    project_list_info_usage: ProjectListInfoUsage,
    mock_project_member_repo: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    current_user_id = 42

    mock_project_member_repo.get_project_ids_by_user_and_roles.side_effect = Exception(
        "DB Connection Lost"
    )

    with pytest.raises(Exception, match="DB Connection Lost"):
        await project_list_info_usage(current_user_id=current_user_id)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()
