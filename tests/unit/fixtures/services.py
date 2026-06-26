from unittest.mock import MagicMock

import pytest

from app.core.auth.jwt import JWTService
from app.core.auth.password import PasswordService


@pytest.fixture
def mock_jwt_service() -> MagicMock:
    service = MagicMock(spec=JWTService)
    service.create_access_token.return_value = "fake.jwt.token"
    return service


@pytest.fixture
def mock_password_service() -> MagicMock:
    return MagicMock(spec=PasswordService)
