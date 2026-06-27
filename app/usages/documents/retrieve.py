from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import HttpUrl

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.role_type import RoleType
from app.core.config import settings
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from app.repositories.document import DocumentRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.document import DocumentDownload
from app.schemas.document import DocumentRead
from app.storage.s3 import S3Storage  # noqa: TC001


class DocumentRetrieveUsage:
    def __init__(
        self,
        repository: DocumentRepository,
        project_member_repository: ProjectMemberAssociationRepository,
        unit_of_work: UnitOfWork,
        s3_storage: S3Storage,
    ) -> None:
        self._repo = repository
        self._project_member_repo = project_member_repository
        self._uow = unit_of_work
        self._storage = s3_storage

    async def __call__(
        self,
        document_id: PositiveInt,
        current_user_id: PositiveInt,
    ) -> DocumentDownload:
        async with self._uow:
            if not (obj := await self._repo.get_by_id(document_id)):
                raise ObjectNotFoundError(obj_id=document_id, table_name="documents")

            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=obj.project_id,
            )

            if not member_association or member_association.role not in {
                RoleType.OWNER,
                RoleType.PARTICIPANT,
            }:
                raise ForbiddenError(AuthorizationErrorMessage.FORBIDDEN)

            document_read = DocumentRead.model_validate(obj)
            s3_key = obj.s3_key
            original_name = obj.original_name

        presigned_url = await self._storage.get_presigned_url(
            key=s3_key,
            original_name=original_name,
            expires_in=settings.s3.presigned_url_expire_seconds,
        )

        return DocumentDownload(
            **document_read.model_dump(), download_url=HttpUrl(presigned_url)
        )
