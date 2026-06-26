from typing import TYPE_CHECKING
from typing import Any

import pytest
from fastapi import status

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.constants.project import ProjectLimits
from app.constants.role_type import RoleType
from app.repositories.project_member import ProjectMemberAssociationRepository
from app.schemas.project_member import ProjectMemberCreateDB
from tests.factories.project import ProjectUpdateReqFactory

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Coroutine

    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.requires_db


async def test_create_project_returns_201_and_sets_creator_id(
    async_client: AsyncClient,
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
    project_payload: dict[str, Any],
) -> None:
    headers, creator_id = await create_user_headers()

    response = await async_client.post(
        "/projects/", json=project_payload, headers=headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == project_payload["name"]
    assert data["description"] == project_payload["description"]
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
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
    project_payload: dict[str, Any],
    invalid_name: str,
    expected_errors_count: int,
) -> None:
    headers, _ = await create_user_headers()
    project_payload["name"] = invalid_name

    response = await async_client.post(
        "/projects/", json=project_payload, headers=headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert len(response.json()["detail"]) == expected_errors_count


async def test_create_project_returns_401_without_bearer_token(
    async_client: AsyncClient,
    project_payload: dict[str, Any],
) -> None:
    response = await async_client.post("/projects/", json=project_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_project_accepts_missing_description(
    async_client: AsyncClient,
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
    project_payload: dict[str, Any],
) -> None:
    headers, _ = await create_user_headers()
    del project_payload["description"]

    response = await async_client.post(
        "/projects/", json=project_payload, headers=headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["description"] is None


async def test_delete_project_returns_204_for_owner(
    async_client: AsyncClient,
    created_project: tuple[int, dict[str, str], int],
) -> None:
    project_id, headers, _ = created_project

    del_resp = await async_client.delete(f"/projects/{project_id}", headers=headers)

    assert del_resp.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_project_returns_403_for_participant(
    async_client: AsyncClient,
    db_session: AsyncSession,
    created_project: tuple[int, dict[str, str], int],
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
) -> None:
    project_id, _, _ = created_project

    participant_headers, participant_id = await create_user_headers()

    repo = ProjectMemberAssociationRepository(db_session)
    await repo.create(
        ProjectMemberCreateDB(
            user_id=participant_id, project_id=project_id, role=RoleType.PARTICIPANT
        )
    )
    await db_session.commit()

    del_resp = await async_client.delete(
        f"/projects/{project_id}", headers=participant_headers
    )

    assert del_resp.status_code == status.HTTP_403_FORBIDDEN
    assert del_resp.json()["detail"] == AuthorizationErrorMessage.FORBIDDEN


async def test_delete_project_returns_403_for_non_member(
    async_client: AsyncClient,
    created_project: tuple[int, dict[str, str], int],
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
) -> None:
    project_id, _, _ = created_project
    intruder_headers, _ = await create_user_headers()

    del_resp = await async_client.delete(
        f"/projects/{project_id}", headers=intruder_headers
    )

    assert del_resp.status_code == status.HTTP_403_FORBIDDEN
    assert del_resp.json()["detail"] == AuthorizationErrorMessage.FORBIDDEN


async def test_update_project_returns_200_for_owner(
    async_client: AsyncClient,
    created_project: tuple[int, dict[str, str], int],
) -> None:
    project_id, headers, _ = created_project
    update_payload = ProjectUpdateReqFactory.build().model_dump()

    update_resp = await async_client.put(
        f"/projects/{project_id}", json=update_payload, headers=headers
    )

    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["name"] == update_payload["name"]


async def test_update_project_returns_200_for_participant(
    async_client: AsyncClient,
    db_session: AsyncSession,
    created_project: tuple[int, dict[str, str], int],
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
) -> None:
    project_id, _, _ = created_project
    participant_headers, participant_id = await create_user_headers()

    repo = ProjectMemberAssociationRepository(db_session)
    await repo.create(
        ProjectMemberCreateDB(
            user_id=participant_id, project_id=project_id, role=RoleType.PARTICIPANT
        )
    )
    await db_session.commit()

    update_payload = ProjectUpdateReqFactory.build().model_dump()
    update_resp = await async_client.put(
        f"/projects/{project_id}", json=update_payload, headers=participant_headers
    )

    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["name"] == update_payload["name"]


async def test_update_project_returns_403_for_non_member(
    async_client: AsyncClient,
    created_project: tuple[int, dict[str, str], int],
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
) -> None:
    project_id, _, _ = created_project
    intruder_headers, _ = await create_user_headers()

    update_payload = ProjectUpdateReqFactory.build().model_dump()

    update_resp = await async_client.put(
        f"/projects/{project_id}", json=update_payload, headers=intruder_headers
    )

    assert update_resp.status_code == status.HTTP_403_FORBIDDEN


async def test_update_project_returns_401_without_token(
    async_client: AsyncClient,
) -> None:
    update_payload = ProjectUpdateReqFactory.build().model_dump()
    resp = await async_client.put("/projects/10", json=update_payload)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
