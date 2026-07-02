import logging
from typing import TYPE_CHECKING
from typing import BinaryIO
from typing import cast

from app.domain.document import EnsureCanCreateDocument  # noqa: TC001
from app.storage.rollback import S3Rollback

if TYPE_CHECKING:
    from fastapi import UploadFile
    from pydantic import PositiveInt

from pydantic import TypeAdapter

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

type S3Key = str
type FileContentType = str

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
        files: list[UploadFile],
        current_user_id: PositiveInt,
    ) -> list[DocumentRead]:
        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=data.project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_create_document(role)

        generated_keys: list[S3Key] = []
        files_for_s3: list[tuple[S3Key, BinaryIO, FileContentType]] = []

        for file in files:
            key_build_data = DocumentKeyBuild(
                original_name=cast("str", file.filename),
                project_id=data.project_id,
            )
            key = self._key_strategy.generate(key_build_data)
            generated_keys.append(key)

            files_for_s3.append((key, file.file, cast("str", file.content_type)))

        await self._storage.upload_files(files_for_s3)

        async with S3Rollback(self._storage, *generated_keys), self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=data.project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_create_document(role)

            create_data_list = [
                DocumentCreateDB(
                    **data.model_dump(),
                    s3_key=key,
                    original_name=cast("str", file.filename),
                )
                for file, key in zip(files, generated_keys, strict=True)
            ]

            objs = await self._repo.bulk_create(create_data_list)
            adapter = TypeAdapter(list[DocumentRead])

            return adapter.validate_python(objs)
