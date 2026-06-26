import pytest
from pydantic import SecretStr

from app.constants.auth import JWTAlgorithm
from app.core.auth.jwt import JWTService
from app.schemas.token import JWTPayload


@pytest.fixture
def jwt_secret() -> str:
    return "super_secret_test_key_for_jwt_123!"


@pytest.fixture
def jwt_service(jwt_secret: str) -> JWTService:
    return JWTService(
        secret=SecretStr(jwt_secret),
        algorithm=JWTAlgorithm.HS256,
        lifetime_seconds=3600,
    )


@pytest.fixture
def valid_payload() -> JWTPayload:
    return JWTPayload(sub="42")
