from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError

if TYPE_CHECKING:
    from app.usages.documents.delete import DocumentDeleteUsage


async def test_document_delete_usage_success(  # noqa: PLR0913
    document_delete_usage: DocumentDeleteUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_delete_document: MagicMock,
    mock_s3_storage: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10
    project_id = 100
    s3_key = "some/s3/key.pdf"

    mock_document = MagicMock(project_id=project_id, s3_key=s3_key)
    mock_document_repo.get_by_id.return_value = mock_document

    mock_role = MagicMock()
    mock_association = MagicMock(role=mock_role)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_association

    await document_delete_usage(document_id=document_id, current_user_id=current_user_id)

    mock_uow.__aenter__.assert_awaited_once()
    mock_document_repo.get_by_id.assert_awaited_once_with(document_id)
    mock_project_member_repo.get_by_user_and_project.assert_awaited_once_with(
        user_id=current_user_id,
        project_id=project_id,
    )
    mock_ensure_can_delete_document.assert_called_once_with(mock_role)
    mock_document_repo.delete.assert_awaited_once_with(document_id)
    mock_uow.__aexit__.assert_awaited_once()

    mock_s3_storage.delete_file.assert_awaited_once_with(s3_key)


async def test_document_delete_usage_fails_when_document_not_found(
    document_delete_usage: DocumentDeleteUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_s3_storage: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10

    mock_document_repo.get_by_id.return_value = None

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await document_delete_usage(
            document_id=document_id, current_user_id=current_user_id
        )

    assert exc_info.value.obj_id == document_id
    assert exc_info.value.table_name == "documents"

    mock_document_repo.get_by_id.assert_awaited_once_with(document_id)
    mock_project_member_repo.get_by_user_and_project.assert_not_called()
    mock_document_repo.delete.assert_not_called()
    mock_s3_storage.delete_file.assert_not_called()


async def test_document_delete_usage_fails_when_user_not_in_project(
    document_delete_usage: DocumentDeleteUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_delete_document: MagicMock,
    mock_s3_storage: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10
    project_id = 100

    mock_document = MagicMock(project_id=project_id)
    mock_document_repo.get_by_id.return_value = mock_document
    mock_project_member_repo.get_by_user_and_project.return_value = None

    mock_ensure_can_delete_document.side_effect = ForbiddenError("Access denied")

    with pytest.raises(ForbiddenError):
        await document_delete_usage(
            document_id=document_id, current_user_id=current_user_id
        )

    mock_ensure_can_delete_document.assert_called_once_with(None)
    mock_document_repo.delete.assert_not_called()
    mock_s3_storage.delete_file.assert_not_called()


async def test_document_delete_usage_fails_when_role_unauthorized(
    document_delete_usage: DocumentDeleteUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_delete_document: MagicMock,
    mock_s3_storage: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10
    project_id = 100

    mock_document = MagicMock(project_id=project_id)
    mock_document_repo.get_by_id.return_value = mock_document

    mock_role = MagicMock()
    mock_association = MagicMock(role=mock_role)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_association

    mock_ensure_can_delete_document.side_effect = ForbiddenError("Access denied")

    with pytest.raises(ForbiddenError):
        await document_delete_usage(
            document_id=document_id, current_user_id=current_user_id
        )

    mock_ensure_can_delete_document.assert_called_once_with(mock_role)
    mock_document_repo.delete.assert_not_called()
    mock_s3_storage.delete_file.assert_not_called()


async def test_document_delete_usage_swallows_s3_error_and_logs(
    document_delete_usage: DocumentDeleteUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_s3_storage: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10
    project_id = 100
    s3_key = "orphaned/s3/key.pdf"

    mock_document = MagicMock(project_id=project_id, s3_key=s3_key)
    mock_document_repo.get_by_id.return_value = mock_document

    mock_role = MagicMock()
    mock_association = MagicMock(role=mock_role)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_association

    boto_error = ClientError(
        {"Error": {"Code": "500", "Message": "Error"}}, "DeleteObject"
    )
    mock_s3_storage.delete_file.side_effect = boto_error

    with patch("app.usages.documents.delete.logger.exception") as mock_logger:
        await document_delete_usage(
            document_id=document_id, current_user_id=current_user_id
        )

    mock_document_repo.delete.assert_awaited_once_with(document_id)
    mock_s3_storage.delete_file.assert_awaited_once_with(s3_key)

    mock_logger.assert_called_once_with(
        "Failed to delete orphaned file from S3. S3 Key: %s", s3_key
    )
