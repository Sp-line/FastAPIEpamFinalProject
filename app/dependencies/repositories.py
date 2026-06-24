from dishka import Provider
from dishka import Scope
from dishka import provide

from app.repositories.unit_of_work import UnitOfWork
from app.repositories.user import UserRepository


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    get_uow = provide(UnitOfWork)

    get_user_repo = provide(UserRepository)
