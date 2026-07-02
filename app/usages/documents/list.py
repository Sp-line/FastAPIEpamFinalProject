from pydantic import PositiveInt
from pydantic import TypeAdapter

from app.domain.document import EnsureCanListDocument  # noqa: TC001
from app.repositories.document import DocumentRepository  # noqa: TC001
from app.repositories.project_member import (
    ProjectMemberAssociationRepository,  # noqa: TC001
)
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.schemas.document import DocumentRead


class DocumentListUsage:
    def __init__(
        self,
        repository: DocumentRepository,
        project_member_repository: ProjectMemberAssociationRepository,
        unit_of_work: UnitOfWork,
        ensure_can_list_document: EnsureCanListDocument,
    ) -> None:
        self._repo = repository
        self._project_member_repo = project_member_repository
        self._uow = unit_of_work
        self._ensure_can_list_document = ensure_can_list_document

    async def __call__(
        self,
        project_id: PositiveInt,
        current_user_id: PositiveInt,
    ) -> list[DocumentRead]:
        async with self._uow:
            member_association = await self._project_member_repo.get_by_user_and_project(
                user_id=current_user_id,
                project_id=project_id,
            )

            role = member_association.role if member_association is not None else None
            self._ensure_can_list_document(role)

            documents_adapter = TypeAdapter(list[DocumentRead])
            documents = await self._repo.get_by_project_id(project_id)

            return documents_adapter.validate_python(documents)
