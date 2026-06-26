from pydantic import PositiveInt
from pydantic import TypeAdapter

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.role_type import RoleType
from app.exceptions.authorization import ForbiddenError
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
    ) -> None:
        self._repo = repository
        self._project_member_repo = project_member_repository
        self._uow = unit_of_work

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

            if not member_association or member_association.role not in {
                RoleType.OWNER,
                RoleType.PARTICIPANT,
            }:
                raise ForbiddenError(AuthorizationErrorMessage.FORBIDDEN)

            documents_adapter = TypeAdapter(list[DocumentRead])
            documents = await self._repo.get_by_project_id(project_id)

            return documents_adapter.validate_python(documents)
