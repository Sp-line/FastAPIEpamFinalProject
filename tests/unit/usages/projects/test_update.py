from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.role_type import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.usages.projects.update import ProjectUpdateUsage


class DummyMemberAssociation:
    def __init__(self, role: RoleType | str) -> None:
        self.role = role


@pytest.fixture
def project_update_usage(
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    mock_uow: MagicMock,
) -> ProjectUpdateUsage:
    return ProjectUpdateUsage(
        repository=mock_project_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
    )


@pytest.mark.parametrize(
    "role",
    [RoleType.OWNER, RoleType.PARTICIPANT],
    ids=["as_owner", "as_participant"],
)
@patch("app.usages.projects.update.ProjectUpdateDB")
@patch("app.usages.projects.update.ProjectRead")
async def test_call_updates_project_successfully(  # noqa: PLR0913
    mock_project_read_class: MagicMock,
    mock_project_update_db_class: MagicMock,
    project_update_usage: ProjectUpdateUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    mock_uow: MagicMock,
    role: RoleType,
) -> None:
    mock_project_member_repo.get_by_user_and_project.return_value = (
        DummyMemberAssociation(role=role)
    )

    mock_updated_orm_model = MagicMock()
    mock_project_repo.update.return_value = mock_updated_orm_model

    mock_req_data = MagicMock()
    mock_req_data.model_dump.return_value = {"name": "Updated Name"}

    result = await project_update_usage(
        project_id=10, data=mock_req_data, current_user_id=42
    )

    mock_uow.__aenter__.assert_awaited_once()
    mock_project_member_repo.get_by_user_and_project.assert_awaited_once_with(
        user_id=42, project_id=10
    )

    mock_project_update_db_class.assert_called_once_with(name="Updated Name")
    mock_project_repo.update.assert_awaited_once_with(
        10, mock_project_update_db_class.return_value
    )

    mock_project_read_class.model_validate.assert_called_once_with(
        mock_updated_orm_model
    )
    assert result == mock_project_read_class.model_validate.return_value


@pytest.mark.parametrize(
    "association",
    [
        None,
        DummyMemberAssociation(role="VIEWER"),
    ],
    ids=["not_a_member", "insufficient_role"],
)
async def test_call_raises_forbidden_error_when_unauthorized(
    project_update_usage: ProjectUpdateUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    association: DummyMemberAssociation | None,
) -> None:
    mock_project_member_repo.get_by_user_and_project.return_value = association
    mock_req_data = MagicMock()

    with pytest.raises(ForbiddenError) as exc_info:
        await project_update_usage(project_id=10, data=mock_req_data, current_user_id=42)

    assert str(exc_info.value) == AuthorizationErrorMessage.FORBIDDEN
    mock_project_repo.update.assert_not_awaited()


async def test_call_raises_object_not_found_when_project_is_missing(
    project_update_usage: ProjectUpdateUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
) -> None:
    with patch("app.usages.projects.update.ProjectUpdateDB"):
        mock_project_member_repo.get_by_user_and_project.return_value = (
            DummyMemberAssociation(role=RoleType.OWNER)
        )
        mock_project_repo.update.return_value = None

        mock_req_data = MagicMock()
        mock_req_data.model_dump.return_value = {"name": "Updated Name"}

        with pytest.raises(ObjectNotFoundError) as exc_info:
            await project_update_usage(
                project_id=10, data=mock_req_data, current_user_id=42
            )

        assert exc_info.value.table_name == "projects"
