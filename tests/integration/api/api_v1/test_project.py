from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from fastapi import status

from app.constants.project import ProjectLimits

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.requires_db


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient) -> tuple[dict[str, str], int]:
    payload = {
        "username": "project_owner",
        "password": "ValidPassword123!",
    }

    create_response = await async_client.post("/auth", json=payload)
    created_user_id = create_response.json()["id"]

    login_response = await async_client.post("/login", data=payload)
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}, created_user_id


async def test_create_project_returns_201_and_sets_creator_id(
    async_client: AsyncClient,
    auth_headers: tuple[dict[str, str], int],
) -> None:
    headers, creator_id = auth_headers
    payload = {
        "name": "Integration project",
        "description": "Project created through HTTP",
    }

    response = await async_client.post("/projects/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["creator_id"] == creator_id
    assert isinstance(data["id"], int)


@pytest.mark.parametrize(
    ("invalid_name", "expected_errors_count"),
    [
        ("A" * (ProjectLimits.NAME_MIN - 1), 1),
        ("B" * (ProjectLimits.NAME_MAX + 1), 1),
    ],
    ids=["name_too_short", "name_too_long"],
)
async def test_create_project_returns_422_for_invalid_name_boundaries(
    async_client: AsyncClient,
    auth_headers: tuple[dict[str, str], int],
    invalid_name: str,
    expected_errors_count: int,
) -> None:
    headers, _ = auth_headers
    payload = {
        "name": invalid_name,
        "description": "Boundary test",
    }

    response = await async_client.post("/projects/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert len(response.json()["detail"]) == expected_errors_count


async def test_create_project_returns_401_without_bearer_token(
    async_client: AsyncClient,
) -> None:
    payload = {
        "name": "No auth project",
        "description": None,
    }

    response = await async_client.post("/projects/", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_project_accepts_missing_description(
    async_client: AsyncClient,
    auth_headers: tuple[dict[str, str], int],
) -> None:
    headers, creator_id = auth_headers
    payload = {
        "name": "Project without description",
    }

    response = await async_client.post("/projects/", json=payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] is None
    assert data["creator_id"] == creator_id
