from unittest.mock import AsyncMock

import pytest

from app.storage.s3 import S3Storage


@pytest.fixture
def mock_s3_storage() -> AsyncMock:
    return AsyncMock(spec=S3Storage)
