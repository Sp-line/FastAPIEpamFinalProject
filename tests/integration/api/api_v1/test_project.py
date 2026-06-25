from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from fastapi import status

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.project import ProjectLimits
from app.constants.role_type import RoleType
from app.repositories.project_member import ProjectMemberAssociationRepository
from app.schemas.project_member import ProjectMemberCreateDB

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

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


async def test_delete_project_returns_204_for_owner(
    async_client: AsyncClient,
    auth_headers: tuple[dict[str, str], int],
) -> None:
    headers, _ = auth_headers

    proj_resp = await async_client.post(
        "/projects/",
        json={"name": "Project to delete", "description": "Temp project"},
        headers=headers,
    )
    project_id = proj_resp.json()["id"]

    del_resp = await async_client.delete(f"/projects/{project_id}", headers=headers)

    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
    assert del_resp.text == ""


async def test_delete_project_returns_403_for_participant(
    async_client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: tuple[dict[str, str], int],
) -> None:
    owner_headers, _ = auth_headers

    proj_resp = await async_client.post(
        "/projects/", json={"name": "Protected Project"}, headers=owner_headers
    )
    project_id = proj_resp.json()["id"]

    intruder_payload = {
        "username": "intruder_participant",
        "password": "ValidPassword123!",
    }
    create_resp = await async_client.post("/auth", json=intruder_payload)
    intruder_id = create_resp.json()["id"]

    login_resp = await async_client.post("/login", data=intruder_payload)
    intruder_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    repo = ProjectMemberAssociationRepository(db_session)
    await repo.create(
        ProjectMemberCreateDB(
            user_id=intruder_id, project_id=project_id, role=RoleType.PARTICIPANT
        )
    )
    await db_session.commit()

    del_resp = await async_client.delete(
        f"/projects/{project_id}", headers=intruder_headers
    )

    assert del_resp.status_code == status.HTTP_403_FORBIDDEN
    assert (
        del_resp.json()["detail"] == AuthorizationErrorMessage.PROJECT_DELETE_FORBIDDEN
    )


async def test_delete_project_returns_403_for_non_member(
    async_client: AsyncClient,
    auth_headers: tuple[dict[str, str], int],
) -> None:
    owner_headers, _ = auth_headers

    proj_resp = await async_client.post(
        "/projects/", json={"name": "Protected Project"}, headers=owner_headers
    )
    project_id = proj_resp.json()["id"]

    intruder_payload = {"username": "intruder_stranger", "password": "ValidPassword123!"}
    await async_client.post("/auth", json=intruder_payload)

    login_resp = await async_client.post("/login", data=intruder_payload)
    intruder_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    del_resp = await async_client.delete(
        f"/projects/{project_id}", headers=intruder_headers
    )

    assert del_resp.status_code == status.HTTP_403_FORBIDDEN
    assert (
        del_resp.json()["detail"] == AuthorizationErrorMessage.PROJECT_DELETE_FORBIDDEN
    )


async def test_delete_project_returns_401_without_token(
    async_client: AsyncClient,
) -> None:
    resp = await async_client.delete("/projects/10")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"] == "Not authenticated"


async def test_delete_project_returns_422_for_invalid_id_type(
    async_client: AsyncClient,
    auth_headers: tuple[dict[str, str], int],
) -> None:
    headers, _ = auth_headers

    resp = await async_client.delete("/projects/not_an_integer", headers=headers)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
