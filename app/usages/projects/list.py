from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import TypeAdapter

from app.domain.project import EnsureCanRetrieveProject  # noqa: TC001

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.repositories.project import ProjectRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.project import ProjectInfoReadWithDocuments


class ProjectListInfoUsage:
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
        current_user_id: PositiveInt,
    ) -> list[ProjectInfoReadWithDocuments]:
        async with self._uow:
            allowed_project_ids = (
                await self._project_member_repo.get_project_ids_by_user_and_roles(
                    user_id=current_user_id,
                    roles=self._ensure_can_retrieve_project.allowed_roles,
                )
            )

            if not allowed_project_ids:
                return []

            projects = await self._repo.get_by_ids_with_documents(allowed_project_ids)

            projects_adapter = TypeAdapter(list[ProjectInfoReadWithDocuments])
            return projects_adapter.validate_python(projects)
