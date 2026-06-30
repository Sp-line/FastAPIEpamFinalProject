from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from app.storage.rollback import S3Rollback


async def test_aenter_returns_s3_rollback_instance(
    s3_rollback: S3Rollback,
) -> None:
    async with s3_rollback as ctx:
        assert ctx is s3_rollback


async def test_aexit_does_not_delete_files_when_no_exception_raised(
    s3_rollback: S3Rollback,
    mock_s3_storage: AsyncMock,
) -> None:
    async with s3_rollback:
        pass

    mock_s3_storage.delete_files.assert_not_called()


async def test_aexit_deletes_files_when_exception_raised(
    s3_rollback: S3Rollback,
    mock_s3_storage: AsyncMock,
) -> None:
    err_msg = "Main context execution failed"

    with pytest.raises(ValueError, match=err_msg):
        async with s3_rollback:
            raise ValueError(err_msg)

    mock_s3_storage.delete_files.assert_called_once_with(
        "test_key_1.txt", "test_key_2.png"
    )


async def test_aexit_suppresses_and_logs_boto_core_error_during_rollback(
    s3_rollback: S3Rollback,
    mock_s3_storage: AsyncMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_s3_storage.delete_files.side_effect = BotoCoreError()
    err_msg = "Main context execution failed"

    with pytest.raises(ValueError, match=err_msg):
        async with s3_rollback:
            raise ValueError(err_msg)

    mock_s3_storage.delete_files.assert_called_once()
    assert "Failed to rollback S3 files after error" in caplog.text


async def test_aexit_suppresses_and_logs_client_error_during_rollback(
    s3_rollback: S3Rollback,
    mock_s3_storage: AsyncMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    error_response: Any = {"Error": {"Code": "InternalError", "Message": "S3 failure"}}
    mock_s3_storage.delete_files.side_effect = ClientError(
        error_response, "DeleteObject"
    )
    err_msg = "Main context execution failed"

    with pytest.raises(ValueError, match=err_msg):
        async with s3_rollback:
            raise ValueError(err_msg)

    mock_s3_storage.delete_files.assert_called_once()
    assert "Failed to rollback S3 files after error" in caplog.text
