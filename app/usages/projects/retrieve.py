from typing import TYPE_CHECKING

from app.domain.project import EnsureCanRetrieveProject  # noqa: TC001

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.exceptions.db import ObjectNotFoundError
from app.repositories.project import ProjectRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.project import ProjectRead


class ProjectRetrieveInfoUsage:
    def __init__(
        self,
        repository: ProjectRepository,
        project_member_repository: ProjectMemberAssociationRepository,
        unit_of_work: UnitOfWork,
        ensure_can_retrieve_project: EnsureCanRetrieveProject,
    ) -> None:
        self._repo = repository
        self._project_member_repo = project_member_repository
        self._uow = unit_of_work
        self._ensure_can_retrieve_project = ensure_can_retrieve_project

    async def __call__(
        self,
        project_id: PositiveInt,
        current_user_id: PositiveInt,
    ) -> ProjectRead:
        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_retrieve_project(role)

            if not (obj := await self._repo.get_by_id(project_id)):
                raise ObjectNotFoundError(obj_id=project_id, table_name="projects")

            return ProjectRead.model_validate(obj)
