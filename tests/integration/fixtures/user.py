from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from fastapi import status

from tests.factories.user import UserCreateReqFactory

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.fixture
def auth_payload() -> dict[str, str]:
    user_req = UserCreateReqFactory.build()

    payload = user_req.model_dump(mode="json")

    payload["password"] = user_req.password.get_secret_value()

    return payload


@pytest_asyncio.fixture(scope="function")
async def registered_user_payload(
    async_client: AsyncClient,
    auth_payload: dict[str, str],
) -> dict[str, str]:
    response = await async_client.post("/auth", json=auth_payload)
    assert response.status_code == status.HTTP_201_CREATED
    auth_payload["id"] = response.json()["id"]
    return auth_payload
