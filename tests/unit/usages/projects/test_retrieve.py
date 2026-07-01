from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.constants import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.schemas.project import ProjectRead
from tests.factories.project import ProjectReadFactory

if TYPE_CHECKING:
    from app.usages.projects.retrieve import ProjectRetrieveInfoUsage


async def test_project_retrieve_info_usage_returns_project_successfully(
    project_retrieve_info_usage: ProjectRetrieveInfoUsage,
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_retrieve_project: MagicMock,
    mock_uow: AsyncMock,
) -> None:
    project_id, current_user_id = 1, 42

    mock_member_assoc = MagicMock(role=RoleType.PARTICIPANT)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_member_assoc

    expected_project_data = ProjectReadFactory.build(id=project_id)

    mock_db_project = MagicMock()
    for key, value in expected_project_data.model_dump().items():
        setattr(mock_db_project, key, value)

    mock_project_repo.get_by_id.return_value = mock_db_project

    result = await project_retrieve_info_usage(
        project_id=project_id, current_user_id=current_user_id
    )

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_project_member_repo.get_by_user_and_project.assert_awaited_once_with(
        user_id=current_user_id,
        project_id=project_id,
    )
    mock_ensure_can_retrieve_project.assert_called_once_with(RoleType.PARTICIPANT)
    mock_project_repo.get_by_id.assert_awaited_once_with(project_id)

    assert isinstance(result, ProjectRead)
    assert result.id == project_id
    assert result.name == expected_project_data.name


async def test_project_retrieve_info_usage_raises_forbidden_if_access_denied(
    project_retrieve_info_usage: ProjectRetrieveInfoUsage,
    mock_project_member_repo: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_ensure_can_retrieve_project: MagicMock,
    mock_uow: AsyncMock,
) -> None:
    project_id, current_user_id = 1, 99

    mock_project_member_repo.get_by_user_and_project.return_value = None

    mock_ensure_can_retrieve_project.side_effect = ForbiddenError()

    with pytest.raises(ForbiddenError):
        await project_retrieve_info_usage(project_id, current_user_id)

    mock_ensure_can_retrieve_project.assert_called_once_with(None)

    mock_project_repo.get_by_id.assert_not_called()

    mock_uow.__aexit__.assert_awaited_once()


async def test_project_retrieve_info_usage_raises_not_found_if_project_missing(
    project_retrieve_info_usage: ProjectRetrieveInfoUsage,
    mock_project_member_repo: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    project_id, current_user_id = 999, 42

    mock_project_member_repo.get_by_user_and_project.return_value = MagicMock(
        role=RoleType.OWNER
    )

    mock_project_repo.get_by_id.return_value = None

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await project_retrieve_info_usage(project_id, current_user_id)

    assert exc_info.value.table_name == "projects"
    assert exc_info.value.obj_id == project_id

    mock_uow.__aexit__.assert_awaited_once()
