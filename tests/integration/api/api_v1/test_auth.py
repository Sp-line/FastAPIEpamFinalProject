from typing import TYPE_CHECKING
from typing import Any

import pytest
from fastapi import status

if TYPE_CHECKING:
    from httpx import AsyncClient

from app.constants.messages.authentication import AuthenticationErrorMessage
from app.constants.messages.db import DBErrorMessage

pytestmark = pytest.mark.requires_db


async def test_user_auth_returns_201_on_success(
    async_client: AsyncClient, auth_payload: dict[str, str]
) -> None:
    response = await async_client.post("/auth", json=auth_payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["username"] == auth_payload["username"]
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.parametrize(
    ("invalid_payload", "expected_errors_count"),
    [
        ({}, 2),
        ({"username": "user"}, 1),
        ({"password": "ValidPassword123!"}, 1),
        ({"username": "user", "password": "123"}, 1),
    ],
    ids=["empty_body", "missing_password", "missing_username", "weak_password"],
)
async def test_user_auth_returns_422_on_invalid_schema(
    async_client: AsyncClient,
    invalid_payload: dict[str, Any],
    expected_errors_count: int,
) -> None:
    response = await async_client.post("/auth", json=invalid_payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert len(response.json()["detail"]) == expected_errors_count


async def test_user_auth_returns_409_conflict_on_duplicate_username(
    async_client: AsyncClient, registered_user_payload: dict[str, str]
) -> None:
    response = await async_client.post("/auth", json=registered_user_payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == DBErrorMessage.UNIQUE_FIELD.format(
        field_name="username"
    )


async def test_user_login_returns_200_and_token_on_success(
    async_client: AsyncClient, registered_user_payload: dict[str, str]
) -> None:
    response = await async_client.post("/login", data=registered_user_payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"  # noqa: S105


async def test_user_login_returns_401_on_invalid_password(
    async_client: AsyncClient, registered_user_payload: dict[str, str]
) -> None:
    invalid_login_data = {**registered_user_payload, "password": "WrongPassword123!"}

    response = await async_client.post("/login", data=invalid_login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        response.json()["detail"] == AuthenticationErrorMessage.INVALID_CREDENTIALS.value
    )
    assert response.headers.get("WWW-Authenticate") == "Bearer"


async def test_user_login_returns_401_on_non_existent_user(
    async_client: AsyncClient, auth_payload: dict[str, str]
) -> None:
    response = await async_client.post("/login", data=auth_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        response.json()["detail"] == AuthenticationErrorMessage.INVALID_CREDENTIALS.value
    )
    assert response.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.parametrize(
    ("invalid_form_data", "expected_errors_count"),
    [
        ({}, 2),
        ({"username": "user"}, 1),
        ({"password": "ValidPassword123!"}, 1),
    ],
    ids=["empty_form", "missing_password", "missing_username"],
)
async def test_user_login_returns_422_on_invalid_form_data(
    async_client: AsyncClient,
    invalid_form_data: dict[str, Any],
    expected_errors_count: int,
) -> None:
    response = await async_client.post("/login", data=invalid_form_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert len(response.json()["detail"]) == expected_errors_count
