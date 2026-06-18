from collections.abc import AsyncIterator  # noqa: TC003

from core.models import database
from dishka import Provider
from dishka import Scope
from dishka import provide
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002


class InfrastructureProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_db_session(self) -> AsyncIterator[AsyncSession]:
        async with database.session_factory() as session:
            yield session
