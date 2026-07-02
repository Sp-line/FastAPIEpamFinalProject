from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.constants import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.schemas.project import ProjectRead
from app.schemas.project import ProjectUpdateDB
from tests.factories.project import ProjectUpdateReqFactory

if TYPE_CHECKING:
    from app.usages.projects.update import ProjectUpdateUsage


async def test_project_update_usage_updates_project_successfully(
    project_update_usage: ProjectUpdateUsage,
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_update_project: MagicMock,
    mock_uow: AsyncMock,
) -> None:
    project_id, current_user_id = 1, 42
    req_data = ProjectUpdateReqFactory.build()

    mock_member_assoc = MagicMock(role=RoleType.OWNER)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_member_assoc

    mock_db_project = MagicMock()
    mock_db_project.id = project_id
    mock_db_project.name = req_data.name or "Old Name"
    mock_db_project.description = req_data.description
    mock_project_repo.update.return_value = mock_db_project

    result = await project_update_usage(
        project_id=project_id, data=req_data, current_user_id=current_user_id
    )

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_ensure_can_update_project.assert_called_once_with(RoleType.OWNER)

    mock_project_repo.update.assert_awaited_once()
    passed_project_id = mock_project_repo.update.call_args.args[0]
    passed_update_db = mock_project_repo.update.call_args.args[1]

    assert passed_project_id == project_id
    assert (
        passed_update_db.model_dump()
        == ProjectUpdateDB(**req_data.model_dump()).model_dump()
    )

    assert isinstance(result, ProjectRead)
    assert result.id == project_id


async def test_project_update_usage_raises_forbidden_if_user_lacks_permission(
    project_update_usage: ProjectUpdateUsage,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_update_project: MagicMock,
    mock_project_repo: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    project_id, current_user_id = 1, 99
    req_data = ProjectUpdateReqFactory.build()

    mock_project_member_repo.get_by_user_and_project.return_value = None

    mock_ensure_can_update_project.side_effect = ForbiddenError()

    with pytest.raises(ForbiddenError):
        await project_update_usage(project_id, req_data, current_user_id)

    mock_ensure_can_update_project.assert_called_once_with(None)

    mock_project_repo.update.assert_not_called()

    mock_uow.__aexit__.assert_awaited_once()


async def test_project_update_usage_raises_not_found_if_project_does_not_exist(
    project_update_usage: ProjectUpdateUsage,
    mock_project_member_repo: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    project_id, current_user_id = 999, 42
    req_data = ProjectUpdateReqFactory.build()

    mock_project_member_repo.get_by_user_and_project.return_value = MagicMock(
        role=RoleType.OWNER
    )

    mock_project_repo.update.return_value = None

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await project_update_usage(project_id, req_data, current_user_id)

    assert exc_info.value.table_name == "projects"
    assert exc_info.value.obj_id == project_id

    mock_uow.__aexit__.assert_awaited_once()
