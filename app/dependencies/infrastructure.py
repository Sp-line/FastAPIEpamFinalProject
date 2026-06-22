from collections.abc import AsyncIterator  # noqa: TC003

from dishka import Provider
from dishka import Scope
from dishka import provide
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from app.core.config import settings
from app.core.models.db import Database


class InfrastructureProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_database(self) -> AsyncIterator[Database]:  # pragma: no cover
        db = Database(
            url=str(settings.db.url),
            echo=settings.db.echo,
            echo_pool=settings.db.echo_pool,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
        )

        yield db

        await db.dispose()

    @provide(scope=Scope.REQUEST)
    async def get_db_session(
        self,
        db: Database,
    ) -> AsyncIterator[AsyncSession]:  # pragma: no cover
        async for session in db.session_getter():
            yield session
