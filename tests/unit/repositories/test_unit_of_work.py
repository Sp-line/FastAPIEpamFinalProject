from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from app.repositories.unit_of_work import UnitOfWork


async def test_aenter_returns_unit_of_work_instance(
    real_uow: UnitOfWork,
) -> None:
    async with real_uow as uow:
        assert uow is real_uow


async def test_aexit_commits_transaction_when_no_exception_raised(
    real_uow: UnitOfWork,
    mock_session: AsyncMock,
) -> None:
    async with real_uow:
        pass

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()


async def test_aexit_rolls_back_transaction_when_exception_raised(
    real_uow: UnitOfWork,
    mock_session: AsyncMock,
) -> None:
    msg = "Test error"
    error = ValueError(msg)

    with pytest.raises(ValueError, match=msg):
        async with real_uow:
            raise error

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
