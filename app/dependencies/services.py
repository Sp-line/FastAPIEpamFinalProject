from dishka import Provider
from dishka import Scope
from dishka import provide

from app.core.auth.jwt import JWTService
from app.core.auth.password import PasswordService
from app.core.config import settings
from app.services.user import UserService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    get_password_service = provide(PasswordService, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_jwt_service(self) -> JWTService:
        return JWTService(
            secret=settings.auth.secret,
            algorithm=settings.auth.algorithm,
            lifetime_seconds=settings.auth.lifetime_seconds,
        )

    get_user_service = provide(UserService)
