from dishka import Provider
from dishka import Scope
from dishka import provide

from app.core.auth.password import PasswordService
from app.services.user import UserService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    get_password_service = provide(PasswordService)

    get_user_service = provide(UserService)
