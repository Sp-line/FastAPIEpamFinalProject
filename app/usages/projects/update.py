from __future__ import annotations

from typing import TYPE_CHECKING

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.role_type import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.repositories.project import ProjectRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.project import ProjectRead
from app.schemas.project import ProjectUpdateDB
from app.schemas.project import ProjectUpdateReq

if TYPE_CHECKING:
    from pydantic import PositiveInt


class ProjectUpdateUsage:
    def __init__(
        self,
        repository: ProjectRepository,
        project_member_repository: ProjectMemberAssociationRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository

    async def __call__(
        self,
        project_id: PositiveInt,
        data: ProjectUpdateReq,
        current_user_id: PositiveInt,
    ) -> ProjectRead:
        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=project_id,
            )

            if not member_association or member_association.role not in {
                RoleType.OWNER,
                RoleType.PARTICIPANT,
            }:
                raise ForbiddenError(AuthorizationErrorMessage.PROJECT_UPDATE_FORBIDDEN)

            update_data = ProjectUpdateDB(**data.model_dump())
            updated_project = await self._repo.update(project_id, update_data)

            if not updated_project:
                raise ObjectNotFoundError(table_name="projects", obj_id=project_id)

            return ProjectRead.model_validate(updated_project)
