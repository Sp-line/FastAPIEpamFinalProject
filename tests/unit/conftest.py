from __future__ import annotations

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from app.constants.auth import JWTAlgorithm
from app.core.auth.jwt import JWTService
from app.core.auth.password import PasswordService
from app.repositories.user import UserRepository
from app.schemas.token import JWTPayload
from app.usages.users.login import UserLoginUsage


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


@pytest.fixture
def mock_jwt_service() -> MagicMock:
    service = MagicMock(spec=JWTService)
    service.create_access_token.return_value = "fake.jwt.token"
    return service


@pytest.fixture
def mock_user_repo() -> MagicMock:
    repo = MagicMock(spec=UserRepository)
    repo.get_by_username = AsyncMock()
    return repo


@pytest.fixture
def mock_password_service() -> MagicMock:
    return MagicMock(spec=PasswordService)


@pytest.fixture
def login_use_case(
    mock_user_repo: MagicMock,
    mock_uow: MagicMock,
    mock_jwt_service: MagicMock,
    mock_password_service: MagicMock,
) -> UserLoginUsage:
    return UserLoginUsage(
        repository=mock_user_repo,
        unit_of_work=mock_uow,
        jwt_service=mock_jwt_service,
        password_service=mock_password_service,
    )


@pytest.fixture
def form_data() -> OAuth2PasswordRequestForm:
    return OAuth2PasswordRequestForm(
        grant_type="password",
        username="test_user",
        password="ValidPassword123!",  # noqa: S106
        scope="",
        client_id=None,
        client_secret=None,
    )


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.execute = AsyncMock()
    return session
