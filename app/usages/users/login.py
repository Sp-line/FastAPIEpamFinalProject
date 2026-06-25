from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.security import OAuth2PasswordRequestForm

from pydantic import SecretStr

from app.core.auth.jwt import JWTService  # noqa: TC001
from app.core.auth.password import PasswordService  # noqa: TC001
from app.exceptions.authentication import InvalidCredentialsError
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.repositories.user import UserRepository  # noqa: TC001
from app.schemas.token import JWTPayload
from app.schemas.token import Token


class UserLoginUsage:
    def __init__(
        self,
        repository: UserRepository,
        unit_of_work: UnitOfWork,
        jwt_service: JWTService,
        password_service: PasswordService,
    ) -> None:
        self._repo = repository
        self._uow = unit_of_work
        self._jwt_service = jwt_service
        self._password_service = password_service

    async def __call__(self, data: OAuth2PasswordRequestForm) -> Token:
        async with self._uow:
            user = await self._repo.get_by_username(data.username)

        if not user or not self._password_service.verify_password(
            SecretStr(data.password), user.hashed_password
        ):
            raise InvalidCredentialsError

        token_payload = JWTPayload(sub=str(user.id))
        access_token = self._jwt_service.create_access_token(payload=token_payload)

        return Token(access_token=access_token)
