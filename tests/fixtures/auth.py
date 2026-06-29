import pytest
from pydantic import SecretStr

from app.constants.auth import JWTAlgorithm
from app.core.auth.jwt import JWTService
from app.schemas.token import JWTPayload


@pytest.fixture
def jwt_secret() -> str:
    return "super_secret_test_key_for_jwt_123!"


@pytest.fixture
def jwt_algorithm() -> JWTAlgorithm:
    return JWTAlgorithm.HS256


@pytest.fixture
def default_lifetime() -> int:
    return 3600


@pytest.fixture
def jwt_service(
    jwt_secret: str, jwt_algorithm: JWTAlgorithm, default_lifetime: int
) -> JWTService:
    return JWTService(
        secret=SecretStr(jwt_secret),
        algorithm=jwt_algorithm,
        lifetime_seconds=default_lifetime,
    )


@pytest.fixture
def valid_payload() -> JWTPayload:
    return JWTPayload(sub="42")
