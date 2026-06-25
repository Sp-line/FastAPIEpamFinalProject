from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
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

from app.core.config import settings
from app.core.models.base import Base
from app.dependencies.infrastructure import InfrastructureProvider
from app.dependencies.repositories import RepositoryProvider
from app.dependencies.services import ServiceProvider
from app.dependencies.usages import UsagesProvider
from app.main import app
from app.repositories.unit_of_work import UnitOfWork
from tests.constants import Messages
from tests.support import should_run_db
from tests.support.dummy_model import DummyModel  # noqa: F401

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator
    from contextlib import AbstractAsyncContextManager

    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncConnection


@pytest.fixture
def mock_uow() -> MagicMock:
    uow = MagicMock(spec=UnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


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

    async with cast(
        "AbstractAsyncContextManager[AsyncConnection]",
        cast("object", engine.begin()),
    ) as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with cast(
        "AbstractAsyncContextManager[AsyncConnection]",
        cast("object", engine.begin()),
    ) as conn:
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
        RepositoryProvider(),
        ServiceProvider(),
        UsagesProvider(),
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
