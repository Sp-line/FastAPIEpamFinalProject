from typing import cast

from dishka import Provider
from dishka import Scope
from dishka import provide
from fastapi_mail import FastMail  # noqa: TC002
from jinja2 import Environment  # noqa: TC002
from types_aiobotocore_ses import SESClient  # noqa: TC002

from app.constants.env_type import EnvironmentType
from app.constants.messages.config import ConfigErrorMessage
from app.core.auth.jwt import JWTService
from app.core.auth.password import PasswordService
from app.core.config import SESMailConfig
from app.core.config import settings
from app.mail.base import EmailService  # noqa: TC001
from app.mail.fastapi_mail import FastAPIMailService
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
        ses_client: SESClient | None,
        fast_mail: FastMail | None,
        jinja_env: Environment,
    ) -> EmailService:
        if settings.env in {EnvironmentType.LOCAL, EnvironmentType.TEST}:
            return FastAPIMailService(fast_mail=cast("FastMail", fast_mail))

        if settings.env == EnvironmentType.PROD:
            ses_config: SESMailConfig = cast("SESMailConfig", settings.email.ses)
            return SESMailService(
                ses_client=cast("SESClient", ses_client),
                sender=ses_config.sender,
                jinja_env=jinja_env,
            )

        raise ValueError(
            ConfigErrorMessage.UNSUPPORTED_ENVIRONMENT.format(env=settings.env)
        )
