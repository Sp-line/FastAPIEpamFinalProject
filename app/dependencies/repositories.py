from dishka import Provider
from dishka import Scope
from dishka import provide

from app.repositories.document import DocumentRepository
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberAssociationRepository
from app.repositories.unit_of_work import UnitOfWork
from app.repositories.user import UserRepository


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    get_uow = provide(UnitOfWork)

    get_user_repo = provide(UserRepository)

    get_project_repo = provide(ProjectRepository)

    get_project_member_repo = provide(ProjectMemberAssociationRepository)

    get_document_repo = provide(DocumentRepository)
