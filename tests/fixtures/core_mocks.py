from unittest.mock import AsyncMock

import pytest

from app.repositories.unit_of_work import UnitOfWork


@pytest.fixture
def mock_uow() -> AsyncMock:
    uow = AsyncMock(spec=UnitOfWork)
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()
