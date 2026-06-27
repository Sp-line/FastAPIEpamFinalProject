from __future__ import annotations

from typing import TYPE_CHECKING

import pytest_asyncio
from dishka import Scope
from dishka import make_async_container
from dishka import provide
from fastapi import FastAPI  # noqa: TC002
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from app.core.config import settings
from app.dependencies.domain import DomainProvider
from app.dependencies.infrastructure import InfrastructureProvider
from app.dependencies.repositories import RepositoryProvider
from app.dependencies.services import ServiceProvider
from app.dependencies.usages import UsagesProvider
from app.main import app

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_app(db_session: AsyncSession) -> AsyncIterator[FastAPI]:
    class TestInfrastructureProvider(InfrastructureProvider):
        @provide(scope=Scope.REQUEST)
        def get_db_session(self) -> AsyncSession:
            return db_session

    test_container = make_async_container(
        TestInfrastructureProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        UsagesProvider(),
        DomainProvider(),
    )

    app.state.dishka_container = test_container

    yield app

    await test_container.close()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def async_client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=test_app)

    base_url = (
        f"{str(settings.test_api.base_url).rstrip('/')}"
        f"{settings.api.prefix}{settings.api.v1.prefix}"
    )

    async with AsyncClient(
        transport=transport,
        base_url=base_url,
    ) as client:
        yield client
