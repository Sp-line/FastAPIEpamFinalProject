from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.core.auth.jwt import JWTService
from app.services.user import UserService


@pytest.fixture
def mock_jwt_service() -> MagicMock:
    service = MagicMock(spec=JWTService)
    service.create_access_token.return_value = "fake.jwt.token"
    return service


@pytest.fixture
def mock_password_service() -> MagicMock:
    mock = MagicMock()
    mock.get_password_hash.return_value = "a" * 50
    return mock


@pytest.fixture
def user_service(
    mock_user_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_password_service: MagicMock,
) -> UserService:
    return UserService(
        repository=mock_user_repo,
        unit_of_work=mock_uow,
        password_service=mock_password_service,
    )
