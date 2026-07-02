from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.constants import RoleType
from app.exceptions.authorization import ForbiddenError
from tests.factories.project import ProjectShareReqFactory

if TYPE_CHECKING:
    from app.core.config import AuthConfig
    from app.schemas.mail import EmailMessage
    from app.schemas.token import InviteJWTPayload
    from app.usages.projects.share import ProjectShareUsage


async def test_project_share_usage_successfully_sends_invitation_email(  # noqa: PLR0913
    project_share_usage: ProjectShareUsage,
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_invite_user: MagicMock,
    mock_jwt_service: MagicMock,
    mock_email_service: AsyncMock,
    mock_url_builder: MagicMock,
    auth_config: AuthConfig,
) -> None:
    project_id, current_user_id = 1, 42
    req_data = ProjectShareReqFactory.build()

    mock_member = MagicMock(role=RoleType.OWNER)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_member

    fake_token = "fake.jwt.token"  # noqa: S105
    mock_jwt_service.create_invite_token.return_value = fake_token

    fake_join_link = f"http://test/join?token={fake_token}"
    mock_url_builder.get_full_endpoint_url.return_value = fake_join_link

    await project_share_usage(
        project_id=project_id,
        data=req_data,
        current_user_id=current_user_id,
    )

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_ensure_can_invite_user.assert_called_once_with(RoleType.OWNER)

    mock_jwt_service.create_invite_token.assert_called_once()
    passed_payload: InviteJWTPayload = (
        mock_jwt_service.create_invite_token.call_args.kwargs["payload"]
    )
    assert passed_payload.sub == req_data.email
    assert passed_payload.project_id == project_id
    assert (
        mock_jwt_service.create_invite_token.call_args.kwargs["lifetime_seconds"]
        == auth_config.invite_lifetime_seconds
    )

    mock_url_builder.get_full_endpoint_url.assert_called_once_with(
        endpoint_url="join",
        resource_prefix="projects",
        query_params={"token": fake_token},
    )

    mock_email_service.send_email.assert_awaited_once()
    passed_msg: EmailMessage = mock_email_service.send_email.call_args.args[0]

    assert passed_msg.recipients == [req_data.email]
    assert passed_msg.template_name == "mail/share.html"
    assert passed_msg.is_html is True
    assert passed_msg.context is not None
    assert passed_msg.context["join_link"] == fake_join_link
    assert (
        passed_msg.context["invite_hours"] == auth_config.invite_lifetime_seconds // 3600
    )


async def test_project_share_usage_raises_forbidden_if_user_lacks_permission(  # noqa: PLR0913
    project_share_usage: ProjectShareUsage,
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_invite_user: MagicMock,
    mock_jwt_service: MagicMock,
    mock_email_service: AsyncMock,
) -> None:
    project_id, current_user_id = 1, 99
    req_data = ProjectShareReqFactory.build()

    mock_project_member_repo.get_by_user_and_project.return_value = None
    mock_ensure_can_invite_user.side_effect = ForbiddenError()

    with pytest.raises(ForbiddenError):
        await project_share_usage(project_id, req_data, current_user_id)

    mock_ensure_can_invite_user.assert_called_once_with(None)

    mock_jwt_service.create_invite_token.assert_not_called()
    mock_email_service.send_email.assert_not_called()

    mock_uow.__aexit__.assert_awaited_once()
