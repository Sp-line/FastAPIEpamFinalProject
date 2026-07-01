from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pydantic import HttpUrl

from app.core.config import settings
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError
from tests.factories.document import DocumentReadFactory

if TYPE_CHECKING:
    from app.usages.documents.retrieve import DocumentRetrieveUsage


async def test_document_retrieve_usage_success_returns_download_schema(  # noqa: PLR0913
    document_retrieve_usage: DocumentRetrieveUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_retrieve_document: MagicMock,
    mock_s3_storage: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10

    expected_read_data = DocumentReadFactory.build()

    document_obj = MagicMock(
        id=expected_read_data.id,
        project_id=expected_read_data.project_id,
        original_name=expected_read_data.original_name,
        s3_key="documents/123/file.pdf",
    )
    mock_document_repo.get_by_id.return_value = document_obj

    mock_role = MagicMock()
    mock_association = MagicMock(role=mock_role)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_association

    fake_presigned_url = "https://fake-s3-bucket.localstack/doc.pdf?signature=123"
    mock_s3_storage.get_presigned_url.return_value = fake_presigned_url

    result = await document_retrieve_usage(
        document_id=document_id,
        current_user_id=current_user_id,
    )

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_document_repo.get_by_id.assert_awaited_once_with(document_id)
    mock_project_member_repo.get_by_user_and_project.assert_awaited_once_with(
        user_id=current_user_id,
        project_id=document_obj.project_id,
    )
    mock_ensure_can_retrieve_document.assert_called_once_with(mock_role)

    mock_s3_storage.get_presigned_url.assert_awaited_once_with(
        key=document_obj.s3_key,
        original_name=document_obj.original_name,
        expires_in=settings.s3.presigned_url_expire_seconds,
    )

    assert result.download_url == HttpUrl(fake_presigned_url)
    assert result.id == expected_read_data.id
    assert result.original_name == expected_read_data.original_name


async def test_document_retrieve_usage_fails_when_document_not_found(
    document_retrieve_usage: DocumentRetrieveUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_s3_storage: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10

    mock_document_repo.get_by_id.return_value = None

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await document_retrieve_usage(
            document_id=document_id,
            current_user_id=current_user_id,
        )

    assert exc_info.value.obj_id == document_id
    assert exc_info.value.table_name == "documents"

    mock_document_repo.get_by_id.assert_awaited_once_with(document_id)
    mock_project_member_repo.get_by_user_and_project.assert_not_called()
    mock_s3_storage.get_presigned_url.assert_not_called()


async def test_document_retrieve_usage_fails_when_user_not_in_project(
    document_retrieve_usage: DocumentRetrieveUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_retrieve_document: MagicMock,
    mock_s3_storage: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10

    document_obj = MagicMock(project_id=100)
    mock_document_repo.get_by_id.return_value = document_obj
    mock_project_member_repo.get_by_user_and_project.return_value = None

    mock_ensure_can_retrieve_document.side_effect = ForbiddenError("Access denied")

    with pytest.raises(ForbiddenError):
        await document_retrieve_usage(
            document_id=document_id,
            current_user_id=current_user_id,
        )

    mock_ensure_can_retrieve_document.assert_called_once_with(None)
    mock_s3_storage.get_presigned_url.assert_not_called()


async def test_document_retrieve_usage_fails_when_role_has_no_permission(
    document_retrieve_usage: DocumentRetrieveUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_retrieve_document: MagicMock,
    mock_s3_storage: AsyncMock,
) -> None:
    document_id = 1
    current_user_id = 10

    document_obj = MagicMock(project_id=100)
    mock_document_repo.get_by_id.return_value = document_obj

    mock_role = MagicMock()
    mock_association = MagicMock(role=mock_role)
    mock_project_member_repo.get_by_user_and_project.return_value = mock_association

    mock_ensure_can_retrieve_document.side_effect = ForbiddenError("Role not allowed")

    with pytest.raises(ForbiddenError):
        await document_retrieve_usage(
            document_id=document_id,
            current_user_id=current_user_id,
        )

    mock_ensure_can_retrieve_document.assert_called_once_with(mock_role)
    mock_s3_storage.get_presigned_url.assert_not_called()
