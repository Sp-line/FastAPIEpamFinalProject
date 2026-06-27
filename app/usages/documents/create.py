import logging
from typing import TYPE_CHECKING

from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

from app.domain.document import EnsureCanCreateDocument  # noqa: TC001

if TYPE_CHECKING:
    from fastapi import UploadFile
    from pydantic import PositiveInt

from app.constants import DocumentMimeType
from app.constants.messages.file import FileErrorMessage
from app.exceptions.file import FileNameError
from app.exceptions.file import FileTypeError
from app.repositories.document import DocumentRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.document import DocumentCreateDB
from app.schemas.document import DocumentCreateReq
from app.schemas.document import DocumentRead
from app.schemas.storage import DocumentKeyBuild
from app.storage.key import DocumentKeyStrategy  # noqa: TC001
from app.storage.s3 import S3Storage  # noqa: TC001

logger = logging.getLogger(__name__)


class DocumentCreateUsage:
    def __init__(  # noqa: PLR0913
        self,
        repository: DocumentRepository,
        project_member_repository: ProjectMemberAssociationRepository,
        unit_of_work: UnitOfWork,
        key_strategy: DocumentKeyStrategy,
        s3_storage: S3Storage,
        ensure_can_create_document: EnsureCanCreateDocument,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._project_member_repo = project_member_repository
        self._storage = s3_storage
        self._key_strategy = key_strategy
        self._ensure_can_create_document = ensure_can_create_document

    async def __call__(
        self,
        data: DocumentCreateReq,
        file: UploadFile,
        current_user_id: PositiveInt,
    ) -> DocumentRead:
        if not file.filename:
            raise FileNameError(FileErrorMessage.FILENAME_MISSING)

        if not file.content_type or file.content_type not in DocumentMimeType:
            raise FileTypeError(
                file_type=file.content_type,
                allowed_types=list(DocumentMimeType),
            )

        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=data.project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_create_document(role)

        key_build_data = DocumentKeyBuild(
            original_name=file.filename,
            project_id=data.project_id,
        )
        key = self._key_strategy.generate(key_build_data)

        await self._storage.upload_file(
            key=key, file_obj=file.file, content_type=file.content_type
        )

        try:
            async with self._uow:
                member_association = (
                    await self._project_member_repo.get_by_user_and_project(
                        user_id=current_user_id,
                        project_id=data.project_id,
                    )
                )

                role = (
                    member_association.role if member_association is not None else None
                )
                self._ensure_can_create_document(role)

                create_data = DocumentCreateDB(
                    **data.model_dump(), s3_key=key, original_name=file.filename
                )

                obj = await self._repo.create(create_data)
                return DocumentRead.model_validate(obj)

        except Exception:
            try:
                await self._storage.delete_file(key)
            except ClientError, BotoCoreError:
                logger.exception(
                    "Failed to delete orphaned S3 file after DB rollback. Key: %s", key
                )

            raise
