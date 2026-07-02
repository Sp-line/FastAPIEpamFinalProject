import pytest
from pydantic import SecretStr

from app.constants.auth import JWTAlgorithm
from app.core.auth.jwt import JWTService
from app.core.config import AuthConfig
from app.schemas.token import JWTPayload


@pytest.fixture
def jwt_secret() -> str:
    return "super_secret_test_key_for_jwt_123!"


@pytest.fixture
def jwt_algorithm() -> JWTAlgorithm:
    return JWTAlgorithm.HS256


@pytest.fixture
def jwt_service(
    jwt_secret: str,
    jwt_algorithm: JWTAlgorithm,
) -> JWTService:
    return JWTService(
        secret=SecretStr(jwt_secret),
        algorithm=jwt_algorithm,
    )


@pytest.fixture
def valid_payload() -> JWTPayload:
    return JWTPayload(sub="42")


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(
        secret=SecretStr("super_secret_test_key_for_jwt_123!"),
        algorithm=JWTAlgorithm.HS256,
        access_lifetime_seconds=60 * 60,
        invite_lifetime_seconds=60 * 60 * 72,
    )
