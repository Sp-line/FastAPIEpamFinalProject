from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
import pytest_asyncio

from tests.factories.project import ProjectCreateReqFactory

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Coroutine

    from httpx import AsyncClient


@pytest.fixture
def project_payload() -> dict[str, Any]:
    return ProjectCreateReqFactory.build().model_dump()


@pytest_asyncio.fixture(scope="function")
async def created_project(
    async_client: AsyncClient,
    create_user_headers: Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]],
    project_payload: dict[str, Any],
) -> tuple[int, dict[str, str], int]:
    owner_headers, owner_id = await create_user_headers()

    response = await async_client.post(
        "/projects/", json=project_payload, headers=owner_headers
    )
    project_id = response.json()["id"]

    return project_id, owner_headers, owner_id
