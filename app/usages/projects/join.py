from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.core.auth.jwt import JWTService  # noqa: TC001
from app.exceptions.db import ObjectNotFoundError
from app.repositories.project import ProjectRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.project_member import ProjectMemberCreateDB
from app.schemas.project_member import ProjectMemberRead


class ProjectJoinUsage:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        jwt_service: JWTService,
        repository: ProjectRepository,
        project_member_repo: ProjectMemberAssociationRepository,
    ) -> None:
        self._uow = unit_of_work
        self._jwt_service = jwt_service
        self._repo = repository
        self._project_member_repo = project_member_repo

    async def __call__(
        self,
        token: str,
        current_user_id: PositiveInt,
    ) -> ProjectMemberRead:
        payload = self._jwt_service.verify_invite_token(token)
        project_id = payload.project_id

        async with self._uow:
            if not await self._repo.get_by_id(project_id):
                raise ObjectNotFoundError(table_name="projects", obj_id=project_id)

            existing_member = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id, project_id=project_id
            )
            if existing_member:
                return ProjectMemberRead.model_validate(existing_member)

            create_db = ProjectMemberCreateDB(
                project_id=project_id,
                user_id=current_user_id,
            )
            new_member = await self._project_member_repo.create(create_db)

        return ProjectMemberRead.model_validate(new_member)
