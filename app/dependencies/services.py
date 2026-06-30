from dishka import Provider
from dishka import Scope
from dishka import provide
from jinja2 import Environment  # noqa: TC002
from types_aiobotocore_ses import SESClient  # noqa: TC002

from app.core.auth.jwt import JWTService
from app.core.auth.password import PasswordService
from app.core.config import settings
from app.mail.base import EmailService  # noqa: TC001
from app.mail.ses import SESMailService
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

    @provide(scope=Scope.APP)
    def get_email_service(
        self,
        ses_client: SESClient,
        jinja_env: Environment,
    ) -> EmailService:
        return SESMailService(
            ses_client=ses_client,
            sender=settings.email.ses.sender,
            jinja_env=jinja_env,
        )
