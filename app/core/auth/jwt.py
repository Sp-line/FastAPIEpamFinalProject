from datetime import UTC
from datetime import datetime
from datetime import timedelta

import jwt
from pydantic import SecretStr
from pydantic import ValidationError

from app.constants.auth import JWTAlgorithm  # noqa: TC001
from app.exceptions.authentication import TokenExpiredError
from app.exceptions.authentication import TokenInvalidError
from app.schemas.token import JWTPayload


class JWTService:
    def __init__(
        self,
        secret: SecretStr,
        algorithm: JWTAlgorithm,
        lifetime_seconds: int,
    ) -> None:
        self.secret = secret
        self.algorithm = algorithm
        self.lifetime_seconds = lifetime_seconds

    def create_access_token(
        self,
        payload: JWTPayload,
        lifetime_seconds: int | None = None,
    ) -> str:
        token_lifetime = (
            lifetime_seconds if lifetime_seconds is not None else self.lifetime_seconds
        )

        payload.exp = datetime.now(UTC) + timedelta(seconds=token_lifetime)

        return jwt.encode(
            payload=payload.model_dump(),
            key=self.secret.get_secret_value(),
            algorithm=self.algorithm,
        )

    def verify_access_token(self, token: str) -> JWTPayload:
        try:
            decoded_data = jwt.decode(
                jwt=token,
                key=self.secret.get_secret_value(),
                algorithms=[self.algorithm],
            )
            return JWTPayload.model_validate(decoded_data)

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError from None
        except jwt.InvalidTokenError, ValidationError:
            raise TokenInvalidError from None
