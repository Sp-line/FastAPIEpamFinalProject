import logging
from typing import TYPE_CHECKING

from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

from app.domain.project import EnsureCanDeleteProject  # noqa: TC001
from app.repositories.document import DocumentRepository  # noqa: TC001
from app.storage.s3 import S3Storage  # noqa: TC001

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.exceptions.db import ObjectNotFoundError
from app.repositories.project import ProjectRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001

logger = logging.getLogger(__name__)


class ProjectDeleteUsage:
    def __init__(  # noqa: PLR0913
        self,
        repository: ProjectRepository,
        unit_of_work: UnitOfWork,
        project_member_repository: ProjectMemberAssociationRepository,
        document_repository: DocumentRepository,
        s3_storage: S3Storage,
        ensure_can_delete_project: EnsureCanDeleteProject,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository
        self._ensure_can_delete_project = ensure_can_delete_project
        self._document_repo = document_repository
        self._storage = s3_storage

    async def __call__(
        self, project_id: PositiveInt, current_user_id: PositiveInt
    ) -> None:
        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_delete_project(role)

            s3_keys = await self._document_repo.get_keys_by_project(project_id)

            if not await self._repo.delete(project_id):
                raise ObjectNotFoundError(obj_id=project_id, table_name="projects")

        if s3_keys:
            try:
                await self._storage.delete_files(*s3_keys)
            except ClientError, BotoCoreError:
                logger.exception(
                    "Failed to batch delete S3 files for project %s", project_id
                )
