from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.exceptions.authorization import ForbiddenError
from tests.factories.document import DocumentReadFactory

if TYPE_CHECKING:
    from app.usages.documents.list import DocumentListUsage


async def test_document_list_usage_success_returns_documents(
    document_list_usage: DocumentListUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_list_document: MagicMock,
) -> None:
    project_id = 1
    current_user_id = 10

    mock_role = MagicMock()
    mock_association = MagicMock(role=mock_role)
    expected_documents = DocumentReadFactory.batch(3)

    mock_project_member_repo.get_by_user_and_project.return_value = mock_association
    mock_document_repo.get_by_project_id.return_value = expected_documents

    result = await document_list_usage(
        project_id=project_id, current_user_id=current_user_id
    )

    mock_project_member_repo.get_by_user_and_project.assert_awaited_once_with(
        user_id=current_user_id,
        project_id=project_id,
    )
    mock_ensure_can_list_document.assert_called_once_with(mock_role)
    mock_document_repo.get_by_project_id.assert_awaited_once_with(project_id)

    assert len(result) == 3  # noqa: PLR2004
    assert result == expected_documents


async def test_document_list_usage_success_returns_empty_list(
    document_list_usage: DocumentListUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
) -> None:
    project_id = 2
    current_user_id = 20

    mock_association = MagicMock(role=MagicMock())
    mock_project_member_repo.get_by_user_and_project.return_value = mock_association
    mock_document_repo.get_by_project_id.return_value = []

    result = await document_list_usage(
        project_id=project_id, current_user_id=current_user_id
    )

    assert result == []
    mock_document_repo.get_by_project_id.assert_awaited_once_with(project_id)


async def test_document_list_usage_fails_when_user_not_in_project(
    document_list_usage: DocumentListUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_list_document: MagicMock,
) -> None:
    project_id = 3
    current_user_id = 30

    mock_project_member_repo.get_by_user_and_project.return_value = None
    mock_ensure_can_list_document.side_effect = ForbiddenError("Access denied")

    with pytest.raises(ForbiddenError):
        await document_list_usage(project_id=project_id, current_user_id=current_user_id)

    mock_ensure_can_list_document.assert_called_once_with(None)

    mock_document_repo.get_by_project_id.assert_not_called()


async def test_document_list_usage_fails_when_role_has_no_permission(
    document_list_usage: DocumentListUsage,
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_ensure_can_list_document: MagicMock,
) -> None:
    project_id = 4
    current_user_id = 40

    mock_role = MagicMock()
    mock_association = MagicMock(role=mock_role)

    mock_project_member_repo.get_by_user_and_project.return_value = mock_association
    mock_ensure_can_list_document.side_effect = ForbiddenError("Role not allowed")

    with pytest.raises(ForbiddenError):
        await document_list_usage(project_id=project_id, current_user_id=current_user_id)

    mock_ensure_can_list_document.assert_called_once_with(mock_role)
    mock_document_repo.get_by_project_id.assert_not_called()


async def test_document_list_usage_uses_unit_of_work(
    document_list_usage: DocumentListUsage,
    mock_project_member_repo: AsyncMock,
    mock_document_repo: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    mock_project_member_repo.get_by_user_and_project.return_value = MagicMock(
        role=MagicMock()
    )
    mock_document_repo.get_by_project_id.return_value = []

    await document_list_usage(project_id=1, current_user_id=1)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()
