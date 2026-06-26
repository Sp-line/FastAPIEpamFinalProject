from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from app.core.config import settings
from app.core.models.base import Base
from tests.constants import Messages
from tests.support import should_run_db

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator
    from contextlib import AbstractAsyncContextManager

    from sqlalchemy.ext.asyncio import AsyncConnection


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
