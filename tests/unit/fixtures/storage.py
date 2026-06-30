from unittest.mock import AsyncMock

import pytest
from types_aiobotocore_s3 import S3Client

from app.storage.rollback import S3Rollback
from app.storage.s3 import S3Storage


@pytest.fixture
def mock_s3_storage() -> AsyncMock:
    return AsyncMock(spec=S3Storage)


@pytest.fixture
def mock_s3_client() -> AsyncMock:
    return AsyncMock(spec=S3Client)


@pytest.fixture
def s3_bucket_name() -> str:
    return "test-epam-bucket"


@pytest.fixture
def s3_storage(mock_s3_client: AsyncMock, s3_bucket_name: str) -> S3Storage:
    return S3Storage(s3_client=mock_s3_client, bucket_name=s3_bucket_name)


@pytest.fixture
def s3_rollback(mock_s3_storage: AsyncMock) -> S3Rollback:
    return S3Rollback(mock_s3_storage, "test_key_1.txt", "test_key_2.png")
