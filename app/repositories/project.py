from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from app.core.models import Project
from app.repositories.base import RepositoryBase
from app.repositories.handlers.project import projects_error_handler
from app.schemas.project import ProjectCreateDB
from app.schemas.project import ProjectUpdateDB


class ProjectRepository(
    RepositoryBase[
        Project,
        ProjectCreateDB,
        ProjectUpdateDB,
    ]
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            model=Project,
            session=session,
            table_error_handler=projects_error_handler,
        )

    async def get_by_ids_with_documents(
        self, project_ids: Sequence[int]
    ) -> Sequence[Project]:
        if not project_ids:
            return []

        stmt = (
            select(self._model)
            .where(self._model.id.in_(project_ids))
            .options(selectinload(self._model.documents))
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
