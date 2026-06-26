from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.role_type import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.repositories.document import DocumentRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.storage.s3 import S3Storage  # noqa: TC001

logger = logging.getLogger(__name__)


class DocumentDeleteUsage:
    def __init__(
        self,
        repository: DocumentRepository,
        unit_of_work: UnitOfWork,
        project_member_repository: ProjectMemberAssociationRepository,
        s3_storage: S3Storage,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository
        self._storage = s3_storage

    async def __call__(
        self,
        document_id: PositiveInt,
        current_user_id: PositiveInt,
    ) -> None:
        async with self._uow:
            if not (obj := await self._repo.get_by_id(document_id)):
                raise ObjectNotFoundError(obj_id=document_id, table_name="documents")

            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=obj.project_id,
            )

            if not member_association or member_association.role != RoleType.OWNER:
                raise ForbiddenError(AuthorizationErrorMessage.FORBIDDEN)

            s3_key = obj.s3_key

            await self._repo.delete(document_id)

        try:
            await self._storage.delete_file(s3_key)
        except BotoCoreError, ClientError:
            logger.exception(
                "Failed to delete orphaned file from S3. S3 Key: %s", s3_key
            )
