from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from fastapi.security import OAuth2PasswordRequestForm

    from app.usages.users.login import UserLoginUsage

import pytest
from pydantic import SecretStr

from app.exceptions.auth import InvalidCredentialsError
from app.schemas.token import Token


class DummyDBUser:
    def __init__(self, obj_id: int, hashed_password: str) -> None:
        self.id = obj_id
        self.hashed_password = hashed_password


async def test_call_returns_token_on_successful_login(  # noqa: PLR0913
    login_use_case: UserLoginUsage,
    mock_user_repo: MagicMock,
    mock_uow: MagicMock,
    mock_password_service: MagicMock,
    mock_jwt_service: MagicMock,
    form_data: OAuth2PasswordRequestForm,
) -> None:
    db_user = DummyDBUser(obj_id=42, hashed_password="hashed_db_password")  # noqa: S106

    mock_user_repo.get_by_username.return_value = db_user
    mock_password_service.verify_password.return_value = True

    token = await login_use_case(form_data)

    mock_uow.__aenter__.assert_awaited_once()

    mock_user_repo.get_by_username.assert_awaited_once_with("test_user")

    mock_password_service.verify_password.assert_called_once_with(
        SecretStr("ValidPassword123!"), "hashed_db_password"
    )

    mock_jwt_service.create_access_token.assert_called_once()
    payload_arg = mock_jwt_service.create_access_token.call_args[1]["payload"]
    assert payload_arg.sub == "42"

    assert isinstance(token, Token)
    assert token.access_token == "fake.jwt.token"  # noqa: S105
    assert token.token_type == "bearer"  # noqa: S105


async def test_call_raises_error_when_user_does_not_exist(
    login_use_case: UserLoginUsage,
    mock_user_repo: MagicMock,
    mock_password_service: MagicMock,
    mock_jwt_service: MagicMock,
    form_data: OAuth2PasswordRequestForm,
) -> None:
    mock_user_repo.get_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError):
        await login_use_case(form_data)

    mock_password_service.verify_password.assert_not_called()
    mock_jwt_service.create_access_token.assert_not_called()


async def test_call_raises_error_when_password_is_incorrect(
    login_use_case: UserLoginUsage,
    mock_user_repo: MagicMock,
    mock_password_service: MagicMock,
    mock_jwt_service: MagicMock,
    form_data: OAuth2PasswordRequestForm,
) -> None:
    db_user = DummyDBUser(obj_id=42, hashed_password="hashed_db_password")  # noqa: S106
    mock_user_repo.get_by_username.return_value = db_user

    mock_password_service.verify_password.return_value = False

    with pytest.raises(InvalidCredentialsError):
        await login_use_case(form_data)

    mock_password_service.verify_password.assert_called_once()
    mock_jwt_service.create_access_token.assert_not_called()
