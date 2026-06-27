from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.project import EnsureCanInviteUser  # noqa: TC001
from app.exceptions.db import ObjectNotFoundError
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.repositories.user import UserRepository  # noqa: TC001
from app.schemas.project_member import ProjectMemberCreateDB
from app.schemas.project_member import ProjectMemberRead

if TYPE_CHECKING:
    from pydantic import PositiveInt

    from app.schemas.project import ProjectInviteReq


class ProjectInviteUsage:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        project_member_repository: ProjectMemberAssociationRepository,
        user_repository: UserRepository,
        ensure_can_invite_user: EnsureCanInviteUser,
    ) -> None:
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository
        self._user_repo = user_repository
        self._ensure_can_invite_user = ensure_can_invite_user

    async def __call__(
        self,
        project_id: PositiveInt,
        data: ProjectInviteReq,
        current_user_id: PositiveInt,
    ) -> ProjectMemberRead:
        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_invite_user(role)

            if not (
                user_to_invite := await self._user_repo.get_by_username(data.username)
            ):
                raise ObjectNotFoundError(
                    table_name="users", conditions={"username": data.username}
                )

            obj = await self._project_member_repo.create(
                ProjectMemberCreateDB(
                    project_id=project_id,
                    user_id=user_to_invite.id,
                )
            )

        return ProjectMemberRead.model_validate(obj)
