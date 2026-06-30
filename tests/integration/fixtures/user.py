from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
import pytest_asyncio
from fastapi import status

from app.core.auth.password import PasswordService
from app.repositories.user import UserRepository
from app.services.user import UserService
from tests.factories.user import UserCreateReqFactory

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Coroutine

    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.repositories.unit_of_work import UnitOfWork


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


@pytest.fixture
def create_user_headers(
    async_client: AsyncClient,
) -> Callable[[], Coroutine[Any, Any, tuple[dict[str, str], int]]]:
    async def _create() -> tuple[dict[str, str], int]:
        user_req = UserCreateReqFactory.build()
        payload = user_req.model_dump(mode="json")
        payload["password"] = user_req.password.get_secret_value()

        create_resp = await async_client.post("/auth", json=payload)
        user_id = create_resp.json()["id"]

        login_resp = await async_client.post("/login", data=payload)
        token = login_resp.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}, user_id

    return _create


@pytest.fixture
def integration_user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)


@pytest.fixture
def password_service() -> PasswordService:
    return PasswordService()


@pytest.fixture
def integration_user_service(
    integration_user_repo: UserRepository,
    real_uow: UnitOfWork,
    password_service: PasswordService,
) -> UserService:
    return UserService(
        repository=integration_user_repo,
        unit_of_work=real_uow,
        password_service=password_service,
    )
