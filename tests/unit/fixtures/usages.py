from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.security import OAuth2PasswordRequestForm

from app.usages.users.login import UserLoginUsage

if TYPE_CHECKING:
    from unittest.mock import AsyncMock
    from unittest.mock import MagicMock


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
def login_use_case(
    mock_user_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_jwt_service: MagicMock,
    mock_password_service: MagicMock,
) -> UserLoginUsage:
    return UserLoginUsage(
        repository=mock_user_repo,
        unit_of_work=mock_uow,
        jwt_service=mock_jwt_service,
        password_service=mock_password_service,
    )
