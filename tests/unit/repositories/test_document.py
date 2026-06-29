from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.constants.db import PostgresErrorCode
from app.core.models.document import Document
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueFieldError
from tests.factories.document import DocumentCreateDBFactory
from tests.factories.document import DocumentUpdateDBFactory

if TYPE_CHECKING:
    from app.repositories.document import DocumentRepository


async def test_get_by_project_id_executes_query_and_returns_models(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    expected_models = [Document(id=1), Document(id=2)]
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    results = await real_document_repo.get_by_project_id(1)

    assert results == expected_models
    mock_session.execute.assert_awaited_once()


async def test_get_keys_by_project_executes_query_and_returns_strings(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    expected_keys = ["project-1/doc1.pdf", "project-1/doc2.pdf"]
    mock_result.scalars.return_value.all.return_value = expected_keys
    mock_session.execute.return_value = mock_result

    results = await real_document_repo.get_keys_by_project(1)

    assert results == expected_keys
    mock_session.execute.assert_awaited_once()


async def test_create_persists_model_and_returns_it(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    document_data = DocumentCreateDBFactory.build()

    result = await real_document_repo.create(document_data)

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
    assert result.original_name == document_data.original_name


@pytest.mark.parametrize(
    ("error_code", "constraint_name", "expected_exception", "expected_field"),
    [
        (PostgresErrorCode.UNIQUE_VIOLATION, "pk_documents", UniqueFieldError, "id"),
        (
            PostgresErrorCode.UNIQUE_VIOLATION,
            "uq_documents_s3_key",
            UniqueFieldError,
            "s3_key",
        ),
        (
            PostgresErrorCode.FOREIGN_KEY_VIOLATION,
            "fk_documents_project_id_projects",
            RelatedObjectNotFoundError,
            "project_id",
        ),
        (
            PostgresErrorCode.CHECK_VIOLATION,
            "ck_documents_check_document_original_name_min_len",
            CheckConstraintError,
            None,
        ),
        (
            PostgresErrorCode.CHECK_VIOLATION,
            "ck_documents_check_document_s3_key_min_len",
            CheckConstraintError,
            None,
        ),
    ],
    ids=[
        "pk_documents",
        "uq_documents_s3_key",
        "fk_documents_project_id_projects",
        "check_document_original_name_min_len",
        "check_document_s3_key_min_len",
    ],
)
async def test_create_raises_mapped_exception_on_integrity_error(  # noqa: PLR0913
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
    error_code: PostgresErrorCode,
    constraint_name: str,
    expected_exception: type[Exception],
    expected_field: str | None,
) -> None:
    document_data = DocumentCreateDBFactory.build()

    orig = MagicMock()
    orig.sqlstate = error_code.value

    cause = MagicMock()
    cause.constraint_name = constraint_name

    orig.__cause__ = cause

    integrity_error = IntegrityError("statement", "params", orig)

    mock_session.flush.side_effect = integrity_error

    with pytest.raises(expected_exception) as exc_info:
        await real_document_repo.create(document_data)

    if expected_field:
        assert getattr(exc_info.value, "field_name", None) == expected_field


async def test_bulk_create_executes_query_and_returns_models(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    documents_data = DocumentCreateDBFactory.batch(2)
    expected_models = [Document(id=1), Document(id=2)]

    mock_result = MagicMock()
    mock_result.all.return_value = expected_models
    mock_session.scalars.return_value = mock_result

    results = await real_document_repo.bulk_create(documents_data)

    assert results == expected_models
    mock_session.scalars.assert_awaited_once()


async def test_get_by_id_returns_model(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    expected_model = Document(id=1)
    mock_session.get.return_value = expected_model

    result = await real_document_repo.get_by_id(1)

    assert result == expected_model
    mock_session.get.assert_awaited_once()


async def test_get_by_ids_returns_models(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    expected_models = [Document(id=1), Document(id=2)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    results = await real_document_repo.get_by_ids([1, 2])

    assert results == expected_models
    mock_session.execute.assert_awaited_once()


async def test_get_all_returns_models(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    expected_models = [Document(id=1), Document(id=2)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    results = await real_document_repo.get_all(skip=0, limit=10)

    assert results == expected_models
    mock_session.execute.assert_awaited_once()


async def test_update_executes_query_and_returns_model(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = DocumentUpdateDBFactory.build()
    expected_model = Document(id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_model
    mock_session.execute.return_value = mock_result

    result = await real_document_repo.update(1, update_data)

    assert result == expected_model
    mock_session.execute.assert_awaited_once()


async def test_delete_executes_query_and_returns_true(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_session.execute.return_value = mock_result

    result = await real_document_repo.delete(1)

    assert result is True
    mock_session.execute.assert_awaited_once()


async def test_delete_returns_false_when_no_rows_affected(
    real_document_repo: DocumentRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_session.execute.return_value = mock_result

    result = await real_document_repo.delete(1)

    assert result is False
    mock_session.execute.assert_awaited_once()
