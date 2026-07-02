from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.core.models.user import User
from app.exceptions.authentication import InvalidCredentialsError
from app.schemas.token import Token

if TYPE_CHECKING:
    from unittest.mock import AsyncMock
    from unittest.mock import MagicMock

    from fastapi.security import OAuth2PasswordRequestForm

    from app.usages.users.login import UserLoginUsage


async def test_call_returns_token_for_valid_credentials(  # noqa: PLR0913
    login_use_case: UserLoginUsage,
    mock_user_repo: AsyncMock,
    mock_password_service: MagicMock,
    mock_jwt_service: MagicMock,
    mock_uow: AsyncMock,
    form_data: OAuth2PasswordRequestForm,
) -> None:
    user_model = User(id=1, username=form_data.username, hashed_password="hashed_pwd")  # noqa: S106
    mock_user_repo.get_by_username.return_value = user_model
    mock_password_service.verify_password.return_value = True
    mock_jwt_service.create_access_token.return_value = "fake_access_token"

    result = await login_use_case(form_data)

    assert isinstance(result, Token)
    assert result.access_token == "fake_access_token"  # noqa: S105
    mock_uow.__aenter__.assert_called_once()
    mock_user_repo.get_by_username.assert_called_once_with(form_data.username)
    mock_password_service.verify_password.assert_called_once()
    mock_jwt_service.create_access_token.assert_called_once()


async def test_call_raises_invalid_credentials_error_when_user_not_found(
    login_use_case: UserLoginUsage,
    mock_user_repo: AsyncMock,
    mock_password_service: MagicMock,
    form_data: OAuth2PasswordRequestForm,
) -> None:
    mock_user_repo.get_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError):
        await login_use_case(form_data)

    mock_user_repo.get_by_username.assert_called_once_with(form_data.username)
    mock_password_service.verify_password.assert_not_called()


async def test_call_raises_invalid_credentials_error_when_password_mismatches(
    login_use_case: UserLoginUsage,
    mock_user_repo: AsyncMock,
    mock_password_service: MagicMock,
    form_data: OAuth2PasswordRequestForm,
) -> None:
    user_model = User(id=1, username=form_data.username, hashed_password="hashed_pwd")  # noqa: S106
    mock_user_repo.get_by_username.return_value = user_model
    mock_password_service.verify_password.return_value = False

    with pytest.raises(InvalidCredentialsError):
        await login_use_case(form_data)

    mock_password_service.verify_password.assert_called_once()
