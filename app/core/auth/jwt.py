from datetime import UTC
from datetime import datetime
from datetime import timedelta

import jwt
from pydantic import SecretStr
from pydantic import ValidationError

from app.constants.auth import JWTAlgorithm  # noqa: TC001
from app.exceptions.authentication import TokenExpiredError
from app.exceptions.authentication import TokenInvalidError
from app.schemas.token import InviteJWTPayload
from app.schemas.token import JWTPayload
from app.schemas.token import JWTPayloadBase


class JWTService:
    def __init__(
        self,
        secret: SecretStr,
        algorithm: JWTAlgorithm,
    ) -> None:
        self.secret = secret
        self.algorithm = algorithm

    def _create_token(self, payload: JWTPayloadBase, lifetime_seconds: int) -> str:
        payload.exp = datetime.now(UTC) + timedelta(seconds=lifetime_seconds)
        return jwt.encode(
            payload=payload.model_dump(),
            key=self.secret.get_secret_value(),
            algorithm=self.algorithm,
        )

    def _verify_token[TJWTPayload: JWTPayloadBase](
        self, token: str, schema: type[TJWTPayload]
    ) -> TJWTPayload:
        try:
            decoded_data = jwt.decode(
                jwt=token,
                key=self.secret.get_secret_value(),
                algorithms=[self.algorithm],
            )
            return schema.model_validate(decoded_data)

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError from None
        except jwt.InvalidTokenError, ValidationError:
            raise TokenInvalidError from None

    def create_access_token(
        self,
        payload: JWTPayload,
        lifetime_seconds: int,
    ) -> str:
        return self._create_token(payload, lifetime_seconds)

    def create_invite_token(
        self,
        payload: InviteJWTPayload,
        lifetime_seconds: int,
    ) -> str:
        return self._create_token(payload, lifetime_seconds)

    def verify_access_token(self, token: str) -> JWTPayload:
        return self._verify_token(token, JWTPayload)

    def verify_invite_token(self, token: str) -> InviteJWTPayload:
        return self._verify_token(token, InviteJWTPayload)
