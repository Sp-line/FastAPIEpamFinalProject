from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.constants import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.schemas.project_member import ProjectMemberCreateDB
from app.schemas.project_member import ProjectMemberRead
from tests.factories.project import ProjectInviteReqFactory
from tests.factories.project_member import ProjectMemberReadFactory

if TYPE_CHECKING:
    from app.usages.projects.invite import ProjectInviteUsage


async def test_project_invite_usage_successfully_invites_user(
    project_invite_usage: ProjectInviteUsage,
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    mock_ensure_can_invite_user: MagicMock,
) -> None:
    project_id = 1
    current_user_id = 42
    invited_user_id = 99

    req_data = ProjectInviteReqFactory.build()

    mock_current_member = MagicMock(role=RoleType.OWNER)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_current_member

    mock_user_to_invite = MagicMock()
    mock_user_to_invite.id = invited_user_id
    mock_user_repo.get_by_username.return_value = mock_user_to_invite

    expected_read_model = ProjectMemberReadFactory.build(
        project_id=project_id, user_id=invited_user_id
    )
    mock_db_member = MagicMock()
    for key, value in expected_read_model.model_dump().items():
        setattr(mock_db_member, key, value)

    mock_project_member_repo.create.return_value = mock_db_member

    result = await project_invite_usage(
        project_id=project_id, data=req_data, current_user_id=current_user_id
    )

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_ensure_can_invite_user.assert_called_once_with(RoleType.OWNER)
    mock_user_repo.get_by_username.assert_awaited_once_with(req_data.username)

    mock_project_member_repo.create.assert_awaited_once()
    created_db_model = mock_project_member_repo.create.call_args.args[0]

    assert isinstance(created_db_model, ProjectMemberCreateDB)
    assert created_db_model.project_id == project_id
    assert created_db_model.user_id == invited_user_id

    assert isinstance(result, ProjectMemberRead)
    assert result.user_id == invited_user_id


async def test_project_invite_usage_raises_forbidden_if_user_lacks_permission(
    project_invite_usage: ProjectInviteUsage,
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    mock_ensure_can_invite_user: MagicMock,
) -> None:
    project_id, current_user_id = 1, 42
    req_data = ProjectInviteReqFactory.build()

    mock_project_member_repo.get_by_user_and_project.return_value = None
    mock_ensure_can_invite_user.side_effect = ForbiddenError()

    with pytest.raises(ForbiddenError):
        await project_invite_usage(project_id, req_data, current_user_id)

    mock_ensure_can_invite_user.assert_called_once_with(None)

    mock_user_repo.get_by_username.assert_not_called()
    mock_project_member_repo.create.assert_not_called()

    mock_uow.__aexit__.assert_awaited_once()


async def test_project_invite_usage_raises_not_found_if_invited_user_missing(
    project_invite_usage: ProjectInviteUsage,
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_user_repo: AsyncMock,
) -> None:
    project_id, current_user_id = 1, 42
    req_data = ProjectInviteReqFactory.build()

    mock_project_member_repo.get_by_user_and_project.return_value = MagicMock(
        role=RoleType.OWNER
    )

    mock_user_repo.get_by_username.return_value = None

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await project_invite_usage(project_id, req_data, current_user_id)

    assert exc_info.value.table_name == "users"

    mock_user_repo.get_by_username.assert_awaited_once_with(req_data.username)

    mock_project_member_repo.create.assert_not_called()

    mock_uow.__aexit__.assert_awaited_once()
