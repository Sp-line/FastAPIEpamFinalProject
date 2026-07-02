from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.exceptions.authentication import TokenInvalidError
from app.exceptions.db import ObjectNotFoundError
from app.schemas.project_member import ProjectMemberCreateDB
from app.schemas.project_member import ProjectMemberRead
from tests.factories.project_member import ProjectMemberReadFactory

if TYPE_CHECKING:
    from app.usages.projects.join import ProjectJoinUsage


async def test_project_join_usage_adds_new_member_successfully(
    project_join_usage: ProjectJoinUsage,
    mock_jwt_service: MagicMock,
    mock_uow: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
) -> None:
    token = "valid.invite.token"  # noqa: S105
    current_user_id = 42
    project_id = 1

    mock_payload = MagicMock()
    mock_payload.project_id = project_id
    mock_jwt_service.verify_invite_token.return_value = mock_payload

    mock_project_repo.get_by_id.return_value = MagicMock(id=project_id)

    mock_project_member_repo.get_by_user_and_project.return_value = None

    expected_member = ProjectMemberReadFactory.build(
        user_id=current_user_id, project_id=project_id
    )
    mock_db_member = MagicMock()
    for key, value in expected_member.model_dump().items():
        setattr(mock_db_member, key, value)
    mock_project_member_repo.create.return_value = mock_db_member

    result = await project_join_usage(token=token, current_user_id=current_user_id)

    mock_jwt_service.verify_invite_token.assert_called_once_with(token)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_project_repo.get_by_id.assert_awaited_once_with(project_id)
    mock_project_member_repo.get_by_user_and_project.assert_awaited_once_with(
        user_id=current_user_id, project_id=project_id
    )

    mock_project_member_repo.create.assert_awaited_once()
    created_db_model = mock_project_member_repo.create.call_args.args[0]
    assert isinstance(created_db_model, ProjectMemberCreateDB)
    assert created_db_model.project_id == project_id
    assert created_db_model.user_id == current_user_id

    assert isinstance(result, ProjectMemberRead)
    assert result.user_id == current_user_id


async def test_project_join_usage_returns_existing_member_if_already_joined(
    project_join_usage: ProjectJoinUsage,
    mock_jwt_service: MagicMock,
    mock_uow: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
) -> None:
    token = "valid.invite.token"  # noqa: S105
    current_user_id = 42
    project_id = 1

    mock_payload = MagicMock(project_id=project_id)
    mock_jwt_service.verify_invite_token.return_value = mock_payload

    mock_project_repo.get_by_id.return_value = MagicMock(id=project_id)

    existing_member_data = ProjectMemberReadFactory.build(
        user_id=current_user_id, project_id=project_id
    )
    mock_existing_db_member = MagicMock()
    for key, value in existing_member_data.model_dump().items():
        setattr(mock_existing_db_member, key, value)

    mock_project_member_repo.get_by_user_and_project.return_value = (
        mock_existing_db_member
    )

    result = await project_join_usage(token=token, current_user_id=current_user_id)

    mock_project_member_repo.create.assert_not_called()

    assert isinstance(result, ProjectMemberRead)
    assert result.user_id == current_user_id

    mock_uow.__aexit__.assert_awaited_once()


async def test_project_join_usage_fails_fast_if_token_is_invalid(
    project_join_usage: ProjectJoinUsage,
    mock_jwt_service: MagicMock,
    mock_uow: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
) -> None:
    token = "invalid.or.expired.token"  # noqa: S105
    current_user_id = 42

    mock_jwt_service.verify_invite_token.side_effect = TokenInvalidError()

    with pytest.raises(TokenInvalidError):
        await project_join_usage(token=token, current_user_id=current_user_id)

    mock_uow.__aenter__.assert_not_called()
    mock_project_repo.get_by_id.assert_not_called()
    mock_project_member_repo.get_by_user_and_project.assert_not_called()


async def test_project_join_usage_raises_not_found_if_project_missing(
    project_join_usage: ProjectJoinUsage,
    mock_jwt_service: MagicMock,
    mock_uow: AsyncMock,
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
) -> None:
    token = "valid.invite.token"  # noqa: S105
    current_user_id = 42
    project_id = 999

    mock_payload = MagicMock(project_id=project_id)
    mock_jwt_service.verify_invite_token.return_value = mock_payload

    mock_project_repo.get_by_id.return_value = None

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await project_join_usage(token=token, current_user_id=current_user_id)

    assert exc_info.value.table_name == "projects"
    assert exc_info.value.obj_id == project_id

    mock_project_member_repo.get_by_user_and_project.assert_not_called()
    mock_project_member_repo.create.assert_not_called()

    mock_uow.__aexit__.assert_awaited_once()
