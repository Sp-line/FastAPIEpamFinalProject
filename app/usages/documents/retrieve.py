from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import HttpUrl

from app.domain.document import EnsureCanRetrieveDocument  # noqa: TC001

if TYPE_CHECKING:
    from pydantic import PositiveInt

from app.core.config import S3Config  # noqa: TC001
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
    def __init__(  # noqa: PLR0913
        self,
        repository: DocumentRepository,
        project_member_repository: ProjectMemberAssociationRepository,
        unit_of_work: UnitOfWork,
        s3_storage: S3Storage,
        ensure_can_retrieve_document: EnsureCanRetrieveDocument,
        s3_config: S3Config,
    ) -> None:
        self._repo = repository
        self._project_member_repo = project_member_repository
        self._uow = unit_of_work
        self._storage = s3_storage
        self._ensure_can_retrieve_document = ensure_can_retrieve_document
        self._s3_config = s3_config

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

            role = member_association.role if member_association is not None else None
            self._ensure_can_retrieve_document(role)

        presigned_url = await self._storage.get_presigned_url(
            key=obj.s3_key,
            original_name=obj.original_name,
            expires_in=self._s3_config.presigned_url_expire_seconds,
        )

        document_read = DocumentRead.model_validate(obj)

        return DocumentDownload(
            **document_read.model_dump(), download_url=HttpUrl(presigned_url)
        )
