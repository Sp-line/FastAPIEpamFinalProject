from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

import jwt
from pydantic import SecretStr  # noqa: TC002

from app.constants.auth import JWTAlgorithm  # noqa: TC001

if TYPE_CHECKING:
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
