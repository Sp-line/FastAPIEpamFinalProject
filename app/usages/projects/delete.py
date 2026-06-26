from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.role_type import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.repositories.project import ProjectRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001


class ProjectDeleteUsage:
    def __init__(
        self,
        repository: ProjectRepository,
        unit_of_work: UnitOfWork,
        project_member_repository: ProjectMemberAssociationRepository,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository

    async def __call__(
        self, project_id: PositiveInt, current_user_id: PositiveInt
    ) -> None:
        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=project_id,
            )

            if not member_association or member_association.role != RoleType.OWNER:
                raise ForbiddenError(AuthorizationErrorMessage.FORBIDDEN)

            if not await self._repo.delete(project_id):
                raise ObjectNotFoundError(obj_id=project_id, table_name="projects")
