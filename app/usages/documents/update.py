import logging
from typing import TYPE_CHECKING
from typing import cast

from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

from app.domain.document import EnsureCanUpdateDocument  # noqa: TC001
from app.storage.rollback import S3Rollback

if TYPE_CHECKING:
    from fastapi import UploadFile
    from pydantic import PositiveInt

from app.exceptions.db import ObjectNotFoundError
from app.repositories.document import DocumentRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.document import DocumentRead
from app.schemas.document import DocumentUpdateDB
from app.schemas.storage import DocumentKeyBuild
from app.storage.key import DocumentKeyStrategy  # noqa: TC001
from app.storage.s3 import S3Storage  # noqa: TC001

logger = logging.getLogger(__name__)


class DocumentUpdateUsage:
    def __init__(  # noqa: PLR0913
        self,
        repository: DocumentRepository,
        project_member_repository: ProjectMemberAssociationRepository,
        unit_of_work: UnitOfWork,
        key_strategy: DocumentKeyStrategy,
        s3_storage: S3Storage,
        ensure_can_update_document: EnsureCanUpdateDocument,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository
        self._storage = s3_storage
        self._key_strategy = key_strategy
        self._ensure_can_update_document = ensure_can_update_document

    async def __call__(
        self,
        document_id: PositiveInt,
        file: UploadFile,
        current_user_id: PositiveInt,
    ) -> DocumentRead:
        async with self._uow:
            if not (old_obj := await self._repo.get_by_id(document_id)):
                raise ObjectNotFoundError(obj_id=document_id, table_name="documents")

            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=old_obj.project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_update_document(role)

        key_build_data = DocumentKeyBuild(
            original_name=cast("str", file.filename),
            project_id=old_obj.project_id,
        )
        new_key = self._key_strategy.generate(key_build_data)

        await self._storage.upload_file(
            key=new_key,
            file_obj=file.file,
            content_type=cast("str", file.content_type),
        )

        async with S3Rollback(self._storage, new_key), self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=old_obj.project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_update_document(role)

            update_data = DocumentUpdateDB(s3_key=new_key, original_name=file.filename)
            updated_obj = await self._repo.update(document_id, update_data)

        try:
            await self._storage.delete_file(old_obj.s3_key)
        except ClientError, BotoCoreError:
            logger.exception(
                "Failed to delete old S3 file after successful update. Key: %s",
                old_obj.s3_key,
            )

        return DocumentRead.model_validate(updated_obj)
