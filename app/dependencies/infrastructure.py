from collections.abc import AsyncIterator  # noqa: TC003

import aioboto3
from dishka import Provider
from dishka import Scope
from dishka import provide
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002
from types_aiobotocore_s3 import S3Client  # noqa: TC002

from app.constants.env_type import EnvironmentType
from app.core.config import settings
from app.core.models.db import Database
from app.storage.key import DocumentKeyStrategy
from app.storage.s3 import S3Storage


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

    @provide(scope=Scope.APP)
    async def get_s3_client(self) -> AsyncIterator[S3Client]:
        client_kwargs: dict[str, str] = {
            "service_name": "s3",
            "region_name": settings.s3.region,
        }

        if settings.env in {EnvironmentType.LOCAL, EnvironmentType.TEST}:
            client_kwargs.update(
                {
                    "endpoint_url": str(settings.s3.endpoint_url),
                    "aws_access_key_id": str(settings.s3.access_key),
                    "aws_secret_access_key": str(settings.s3.secret_key),
                }
            )

        session = aioboto3.Session()
        async with session.client(**client_kwargs) as client:
            yield client

    @provide(scope=Scope.APP)
    def get_s3_storage(self, s3_client: S3Client) -> S3Storage:
        return S3Storage(s3_client=s3_client, bucket_name=settings.s3.bucket_name)

    get_document_key_strategy = provide(DocumentKeyStrategy, scope=Scope.APP)
