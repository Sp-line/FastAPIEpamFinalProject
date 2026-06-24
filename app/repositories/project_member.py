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
