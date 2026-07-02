from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

if TYPE_CHECKING:
    from unittest.mock import Mock

    from app.core.auth.jwt import JWTService

import pytest

from app.dependencies.auth import extract_user_id_from_token
from app.exceptions.authentication import TokenExpiredError
from app.exceptions.authentication import TokenInvalidError
from app.schemas.token import JWTPayload

TEST_USER_ID = 42


async def test_extract_user_id_returns_int_on_valid_token(
    mock_jwt_service: Mock,
) -> None:
    mock_jwt_service.verify_access_token.return_value = JWTPayload(sub=str(TEST_USER_ID))
    mock_token = "fake.valid.token"  # noqa: S105

    result = await extract_user_id_from_token(
        token=mock_token,
        jwt_service=cast("JWTService", mock_jwt_service),
    )

    assert isinstance(result, int)
    assert result == TEST_USER_ID
    mock_jwt_service.verify_access_token.assert_called_once_with(mock_token)


async def test_extract_user_id_propagates_expired_error(
    mock_jwt_service: Mock,
) -> None:
    mock_jwt_service.verify_access_token.side_effect = TokenExpiredError()
    mock_token = "fake.expired.token"  # noqa: S105

    with pytest.raises(TokenExpiredError):
        await extract_user_id_from_token(
            token=mock_token,
            jwt_service=cast("JWTService", mock_jwt_service),
        )


async def test_extract_user_id_propagates_invalid_error(
    mock_jwt_service: Mock,
) -> None:
    mock_jwt_service.verify_access_token.side_effect = TokenInvalidError()
    mock_token = "fake.invalid.token"  # noqa: S105

    with pytest.raises(TokenInvalidError):
        await extract_user_id_from_token(
            token=mock_token,
            jwt_service=cast("JWTService", mock_jwt_service),
        )
