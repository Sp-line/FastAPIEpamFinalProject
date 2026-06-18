from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from core.config import settings
from dishka import Scope
from dishka import make_async_container
from dishka import provide
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from app.core.models.base import Base
from app.dependencies.infrastructure import InfrastructureProvider
from app.main import app
from tests.constants import Messages
from tests.utils import should_run_db

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator

    from fastapi import FastAPI


@pytest.fixture(scope="session")
def postgres_url(request: pytest.FixtureRequest) -> Iterator[str]:
    if not should_run_db(request):
        pytest.skip(Messages.SKIP_DB_INITIALIZATION)

    image = settings.test_db.image
    driver = settings.test_db.driver

    with PostgresContainer(image, driver=driver) as postgres:
        yield postgres.get_connection_url()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine(
    postgres_url: str,
    request: pytest.FixtureRequest,
) -> AsyncIterator[AsyncEngine]:
    if not should_run_db(request):
        pytest.skip(Messages.SKIP_DB_INITIALIZATION)

    engine = create_async_engine(postgres_url, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async with test_engine.connect() as conn:
        trans = await conn.begin()

        async_session = AsyncSession(
            conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        yield async_session

        await async_session.close()
        await trans.rollback()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_app(db_session: AsyncSession) -> AsyncIterator[FastAPI]:
    class TestInfrastructureProvider(InfrastructureProvider):
        @provide(scope=Scope.REQUEST)
        def get_db_session(self) -> AsyncSession:
            return db_session

    test_container = make_async_container(
        TestInfrastructureProvider(),
    )

    app.state.dishka_container = test_container

    yield app

    await test_container.close()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def async_client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url=str(settings.test_api.base_url),
    ) as client:
        yield client
