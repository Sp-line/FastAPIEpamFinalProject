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
