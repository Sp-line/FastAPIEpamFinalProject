from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.constants import RoleType
from app.repositories.project import ProjectRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.project import ProjectCreateDB
from app.schemas.project import ProjectCreateReq
from app.schemas.project import ProjectRead
from app.schemas.project_member import ProjectMemberCreateDB


class ProjectCreateUsage:
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
        self, data: ProjectCreateReq, creator_id: PositiveInt
    ) -> ProjectRead:
        async with self._uow:
            project_create_data = ProjectCreateDB(
                **data.model_dump(), creator_id=creator_id
            )
            obj = await self._repo.create(project_create_data)

            project_member_create_data = ProjectMemberCreateDB(
                role=RoleType.OWNER,
                user_id=creator_id,
                project_id=obj.id,
            )

            await self._project_member_repo.create(project_member_create_data)
            return ProjectRead.model_validate(obj)
