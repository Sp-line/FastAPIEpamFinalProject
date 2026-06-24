from unittest.mock import AsyncMock

import pytest

from app.repositories.unit_of_work import UnitOfWork


class DummyTestError(Exception):
    pass


async def test_unit_of_work_commits_on_successful_execution() -> None:
    mock_session = AsyncMock()
    uow = UnitOfWork(session=mock_session)

    async with uow:
        pass

    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_not_awaited()


async def test_unit_of_work_rolls_back_on_exception() -> None:
    mock_session = AsyncMock()
    uow = UnitOfWork(session=mock_session)

    with pytest.raises(DummyTestError):
        async with uow:
            raise DummyTestError

    mock_session.rollback.assert_awaited_once()
    mock_session.commit.assert_not_awaited()
