from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.auth.jwt import JWTService  # noqa: TC001
from app.core.config import AuthConfig  # noqa: TC001
from app.domain.project import EnsureCanInviteUser  # noqa: TC001
from app.mail.base import EmailService  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.mail import EmailMessage
from app.schemas.token import InviteJWTPayload
from app.utils.url import UrlBuilder  # noqa: TC001

if TYPE_CHECKING:
    from pydantic import PositiveInt

    from app.schemas.project import ProjectShareReq


class ProjectShareUsage:
    def __init__(  # noqa: PLR0913
        self,
        unit_of_work: UnitOfWork,
        project_member_repo: ProjectMemberAssociationRepository,
        ensure_can_invite: EnsureCanInviteUser,
        jwt_service: JWTService,
        email_service: EmailService,
        url_builder: UrlBuilder,
        auth_config: AuthConfig,
    ) -> None:
        self._uow = unit_of_work
        self._project_member_repo = project_member_repo
        self._ensure_can_invite = ensure_can_invite
        self._jwt_service = jwt_service
        self._email_service = email_service
        self._url_builder = url_builder
        self._auth_config = auth_config

    async def __call__(
        self,
        project_id: PositiveInt,
        data: ProjectShareReq,
        current_user_id: PositiveInt,
    ) -> None:
        async with self._uow:
            member = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id, project_id=project_id
            )
            role = member.role if member is not None else None
            self._ensure_can_invite(role)

        lifetime_seconds = self._auth_config.invite_lifetime_seconds
        payload = InviteJWTPayload(sub=data.email, project_id=project_id)
        token = self._jwt_service.create_invite_token(
            payload=payload,
            lifetime_seconds=lifetime_seconds,
        )

        join_link = self._url_builder.get_full_endpoint_url(
            endpoint_url="join",
            resource_prefix="projects",
            query_params={"token": token},
        )

        lifetime_hours = lifetime_seconds // 3600

        msg = EmailMessage(
            subject="You are invited to join a project!",
            recipients=[data.email],
            is_html=True,
            template_name="mail/share.html",
            context={"join_link": join_link, "invite_hours": lifetime_hours},
        )

        await self._email_service.send_email(msg)
