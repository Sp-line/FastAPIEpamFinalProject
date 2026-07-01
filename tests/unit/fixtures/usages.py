from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.security import OAuth2PasswordRequestForm

from app.usages.documents.delete import DocumentDeleteUsage
from app.usages.documents.list import DocumentListUsage
from app.usages.documents.retrieve import DocumentRetrieveUsage
from app.usages.projects.create import ProjectCreateUsage
from app.usages.projects.delete import ProjectDeleteUsage
from app.usages.projects.invite import ProjectInviteUsage
from app.usages.projects.list import ProjectListInfoUsage
from app.usages.projects.retrieve import ProjectRetrieveInfoUsage
from app.usages.projects.update import ProjectUpdateUsage
from app.usages.users.login import UserLoginUsage

if TYPE_CHECKING:
    from unittest.mock import AsyncMock
    from unittest.mock import MagicMock


@pytest.fixture
def form_data() -> OAuth2PasswordRequestForm:
    return OAuth2PasswordRequestForm(
        grant_type="password",
        username="test_user",
        password="ValidPassword123!",  # noqa: S106
        scope="",
        client_id=None,
        client_secret=None,
    )


@pytest.fixture
def login_use_case(
    mock_user_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_jwt_service: MagicMock,
    mock_password_service: MagicMock,
) -> UserLoginUsage:
    return UserLoginUsage(
        repository=mock_user_repo,
        unit_of_work=mock_uow,
        jwt_service=mock_jwt_service,
        password_service=mock_password_service,
    )


@pytest.fixture
def project_create_usage(
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_uow: AsyncMock,
) -> ProjectCreateUsage:
    return ProjectCreateUsage(
        repository=mock_project_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
    )


@pytest.fixture
def project_delete_usage(  # noqa: PLR0913
    mock_project_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_document_repo: AsyncMock,
    mock_s3_storage: AsyncMock,
    mock_ensure_can_delete_project: MagicMock,
) -> ProjectDeleteUsage:
    return ProjectDeleteUsage(
        repository=mock_project_repo,
        unit_of_work=mock_uow,
        project_member_repository=mock_project_member_repo,
        document_repository=mock_document_repo,
        s3_storage=mock_s3_storage,
        ensure_can_delete_project=mock_ensure_can_delete_project,
    )


@pytest.fixture
def project_update_usage(
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_ensure_can_update_project: MagicMock,
) -> ProjectUpdateUsage:
    return ProjectUpdateUsage(
        repository=mock_project_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
        ensure_can_update_project=mock_ensure_can_update_project,
    )


@pytest.fixture
def project_list_info_usage(
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_ensure_can_retrieve_project: MagicMock,
) -> ProjectListInfoUsage:
    return ProjectListInfoUsage(
        repository=mock_project_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
        ensure_can_retrieve_project=mock_ensure_can_retrieve_project,
    )


@pytest.fixture
def project_retrieve_info_usage(
    mock_project_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_ensure_can_retrieve_project: MagicMock,
) -> ProjectRetrieveInfoUsage:
    return ProjectRetrieveInfoUsage(
        repository=mock_project_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
        ensure_can_retrieve_project=mock_ensure_can_retrieve_project,
    )


@pytest.fixture
def project_invite_usage(
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    mock_ensure_can_invite_user: MagicMock,
) -> ProjectInviteUsage:
    return ProjectInviteUsage(
        unit_of_work=mock_uow,
        project_member_repository=mock_project_member_repo,
        user_repository=mock_user_repo,
        ensure_can_invite_user=mock_ensure_can_invite_user,
    )


@pytest.fixture
def document_list_usage(
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_ensure_can_list_document: MagicMock,
) -> DocumentListUsage:
    return DocumentListUsage(
        repository=mock_document_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
        ensure_can_list_document=mock_ensure_can_list_document,
    )


@pytest.fixture
def document_delete_usage(
    mock_document_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_s3_storage: AsyncMock,
    mock_ensure_can_delete_document: MagicMock,
) -> DocumentDeleteUsage:
    return DocumentDeleteUsage(
        repository=mock_document_repo,
        unit_of_work=mock_uow,
        project_member_repository=mock_project_member_repo,
        s3_storage=mock_s3_storage,
        ensure_can_delete_document=mock_ensure_can_delete_document,
    )


@pytest.fixture
def document_retrieve_usage(
    mock_document_repo: AsyncMock,
    mock_project_member_repo: AsyncMock,
    mock_uow: AsyncMock,
    mock_s3_storage: AsyncMock,
    mock_ensure_can_retrieve_document: MagicMock,
) -> DocumentRetrieveUsage:
    return DocumentRetrieveUsage(
        repository=mock_document_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
        s3_storage=mock_s3_storage,
        ensure_can_retrieve_document=mock_ensure_can_retrieve_document,
    )
