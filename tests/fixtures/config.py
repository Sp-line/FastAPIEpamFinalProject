import pytest
from pydantic import SecretStr

from app.constants.auth import JWTAlgorithm
from app.core.config import AuthConfig
from app.core.config import S3Config


@pytest.fixture
def s3_config() -> S3Config:
    return S3Config(
        bucket_name="test-bucket",
        region="us-east-1",
        presigned_url_expire_seconds=60 * 5,
    )


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(
        secret=SecretStr("super_secret_test_key_for_jwt_123!"),
        algorithm=JWTAlgorithm.HS256,
        access_lifetime_seconds=60 * 60,
        invite_lifetime_seconds=60 * 60 * 72,
    )
