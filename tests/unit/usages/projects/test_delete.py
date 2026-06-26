from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import MagicMock

import pytest

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.role_type import RoleType
from app.exceptions.authorization import ForbiddenError
from app.usages.projects.delete import ProjectDeleteUsage


class DummyMemberAssociation:
    def __init__(self, role: RoleType) -> None:
        self.role = role


@pytest.fixture
def project_delete_usage(
    mock_project_repo: MagicMock,
    mock_uow: MagicMock,
    mock_project_member_repo: MagicMock,
) -> ProjectDeleteUsage:
    return ProjectDeleteUsage(
        repository=mock_project_repo,
        unit_of_work=mock_uow,
        project_member_repository=mock_project_member_repo,
    )


async def test_call_deletes_project_when_user_is_owner(
    project_delete_usage: ProjectDeleteUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    mock_uow: MagicMock,
) -> None:
    mock_project_member_repo.get_by_user_and_project.return_value = (
        DummyMemberAssociation(role=RoleType.OWNER)
    )

    await project_delete_usage(project_id=10, current_user_id=42)

    mock_uow.__aenter__.assert_awaited_once()
    mock_project_member_repo.get_by_user_and_project.assert_awaited_once_with(
        user_id=42, project_id=10
    )
    mock_project_repo.delete.assert_awaited_once_with(10)


@pytest.mark.parametrize(
    "returned_association",
    [
        None,
        DummyMemberAssociation(role=RoleType.PARTICIPANT),
    ],
    ids=["not_a_member", "wrong_role_participant"],
)
async def test_call_raises_forbidden_error_when_unauthorized(
    project_delete_usage: ProjectDeleteUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    returned_association: DummyMemberAssociation | None,
) -> None:
    mock_project_member_repo.get_by_user_and_project.return_value = returned_association

    with pytest.raises(ForbiddenError) as exc_info:
        await project_delete_usage(project_id=10, current_user_id=42)

    assert str(exc_info.value) == AuthorizationErrorMessage.FORBIDDEN

    mock_project_repo.delete.assert_not_awaited()
