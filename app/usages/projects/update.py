from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.project import EnsureCanUpdateProject  # noqa: TC001
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
        ensure_can_update_project: EnsureCanUpdateProject,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository
        self._ensure_can_update_project = ensure_can_update_project

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

            role = member_association.role if member_association is not None else None
            self._ensure_can_update_project(role)

            update_data = ProjectUpdateDB(**data.model_dump())

            if not (updated_project := await self._repo.update(project_id, update_data)):
                raise ObjectNotFoundError(table_name="projects", obj_id=project_id)

            return ProjectRead.model_validate(updated_project)
