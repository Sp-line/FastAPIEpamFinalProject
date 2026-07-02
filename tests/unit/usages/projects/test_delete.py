from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

from app.constants import RoleType
from app.exceptions.authorization import ForbiddenError
from app.exceptions.db import ObjectNotFoundError

if TYPE_CHECKING:
    from app.usages.projects.delete import ProjectDeleteUsage


class TestProjectDeleteUsage:
    async def test_project_delete_usage_success_with_s3_files(  # noqa: PLR0913
        self,
        project_delete_usage: ProjectDeleteUsage,
        mock_project_repo: AsyncMock,
        mock_project_member_repo: AsyncMock,
        mock_document_repo: AsyncMock,
        mock_ensure_can_delete_project: MagicMock,
        mock_s3_storage: AsyncMock,
        mock_uow: AsyncMock,
    ) -> None:
        project_id, current_user_id = 1, 42
        s3_keys = ["proj_1/doc1.pdf", "proj_1/doc2.pdf"]

        mock_member_assoc = MagicMock(role=RoleType.OWNER)
        mock_project_member_repo.get_by_user_and_project.return_value = mock_member_assoc
        mock_document_repo.get_keys_by_project.return_value = s3_keys
        mock_project_repo.delete.return_value = True

        await project_delete_usage(project_id, current_user_id)

        mock_uow.__aenter__.assert_awaited_once()
        mock_uow.__aexit__.assert_awaited_once()

        mock_ensure_can_delete_project.assert_called_once_with(RoleType.OWNER)

        mock_project_repo.delete.assert_awaited_once_with(project_id)

        mock_s3_storage.delete_files.assert_awaited_once_with(*s3_keys)

    async def test_project_delete_usage_success_without_s3_files(  # noqa: PLR0913
        self,
        project_delete_usage: ProjectDeleteUsage,
        mock_project_repo: AsyncMock,
        mock_project_member_repo: AsyncMock,
        mock_document_repo: AsyncMock,
        mock_ensure_can_delete_project: MagicMock,
        mock_s3_storage: AsyncMock,
    ) -> None:
        project_id, current_user_id = 1, 42

        mock_project_member_repo.get_by_user_and_project.return_value = None
        mock_document_repo.get_keys_by_project.return_value = []
        mock_project_repo.delete.return_value = True

        await project_delete_usage(project_id, current_user_id)

        mock_ensure_can_delete_project.assert_called_once_with(None)
        mock_project_repo.delete.assert_awaited_once_with(project_id)
        mock_s3_storage.delete_files.assert_not_called()

    async def test_project_delete_usage_raises_forbidden_if_unauthorized(
        self,
        project_delete_usage: ProjectDeleteUsage,
        mock_project_member_repo: AsyncMock,
        mock_ensure_can_delete_project: MagicMock,
        mock_project_repo: AsyncMock,
        mock_s3_storage: AsyncMock,
    ) -> None:
        mock_project_member_repo.get_by_user_and_project.return_value = MagicMock(
            role=RoleType.PARTICIPANT
        )
        mock_ensure_can_delete_project.side_effect = ForbiddenError()

        with pytest.raises(ForbiddenError):
            await project_delete_usage(1, 42)

        mock_project_repo.delete.assert_not_called()
        mock_s3_storage.delete_files.assert_not_called()

    async def test_project_delete_usage_raises_not_found_if_project_missing(
        self,
        project_delete_usage: ProjectDeleteUsage,
        mock_project_member_repo: AsyncMock,
        mock_project_repo: AsyncMock,
        mock_document_repo: AsyncMock,
        mock_s3_storage: AsyncMock,
    ) -> None:
        mock_project_member_repo.get_by_user_and_project.return_value = MagicMock(
            role=RoleType.OWNER
        )
        mock_document_repo.get_keys_by_project.return_value = ["file.pdf"]
        mock_project_repo.delete.return_value = False

        with pytest.raises(ObjectNotFoundError) as exc_info:
            await project_delete_usage(1, 42)

        assert exc_info.value.table_name == "projects"
        mock_s3_storage.delete_files.assert_not_called()

    @pytest.mark.parametrize(
        "s3_exception",
        [
            BotoCoreError(),
            ClientError(error_response={"Error": {}}, operation_name="DeleteObjects"),
        ],
        ids=["botocore_error", "client_error"],
    )
    async def test_project_delete_usage_swallows_s3_errors_and_logs(  # noqa: PLR0913
        self,
        project_delete_usage: ProjectDeleteUsage,
        mock_project_repo: AsyncMock,
        mock_project_member_repo: AsyncMock,
        mock_document_repo: AsyncMock,
        mock_s3_storage: AsyncMock,
        s3_exception: Exception,
    ) -> None:
        project_id, current_user_id = 1, 42
        mock_project_member_repo.get_by_user_and_project.return_value = MagicMock(
            role=RoleType.OWNER
        )
        mock_document_repo.get_keys_by_project.return_value = ["file1", "file2"]
        mock_project_repo.delete.return_value = True

        mock_s3_storage.delete_files.side_effect = s3_exception

        with patch("app.usages.projects.delete.logger") as mock_logger:
            await project_delete_usage(project_id, current_user_id)

        mock_project_repo.delete.assert_awaited_once_with(project_id)
        mock_logger.exception.assert_called_once_with(
            "Failed to batch delete S3 files for project %s", project_id
        )
