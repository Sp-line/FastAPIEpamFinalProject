from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from app.constants.role_type import RoleType

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from app.core.models.project_member import ProjectMemberAssociation
from app.repositories.base import RepositoryBase
from app.repositories.handlers.project_member import (
    project_member_associations_error_handler,
)
from app.schemas.project_member import ProjectMemberCreateDB
from app.schemas.project_member import ProjectMemberUpdateDB


class ProjectMemberAssociationRepository(
    RepositoryBase[
        ProjectMemberAssociation,
        ProjectMemberCreateDB,
        ProjectMemberUpdateDB,
    ]
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            model=ProjectMemberAssociation,
            session=session,
            table_error_handler=project_member_associations_error_handler,
        )

    async def get_by_user_and_project(
        self,
        user_id: int,
        project_id: int,
    ) -> ProjectMemberAssociation | None:
        stmt = select(ProjectMemberAssociation).where(
            ProjectMemberAssociation.user_id == user_id,
            ProjectMemberAssociation.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_project_ids_by_user_and_roles(
        self, user_id: int, roles: set[RoleType]
    ) -> Sequence[int]:
        if not roles:
            return []

        stmt = select(self._model.project_id).where(
            self._model.user_id == user_id, self._model.role.in_(roles)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
