from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.constants.db import PostgresErrorCode
from app.core.models.project import Project
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueFieldError

if TYPE_CHECKING:
    from app.repositories.project import ProjectRepository

from app.schemas.project import ProjectUpdateDB
from tests.factories.project import ProjectCreateDBFactory
from tests.factories.project import ProjectUpdateDBFactory


async def test_get_by_ids_with_documents_returns_models(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    expected_models = [Project(id=1), Project(id=2)]
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    result = await real_project_repo.get_by_ids_with_documents([1, 2])

    assert result == expected_models
    mock_session.execute.assert_called_once()


async def test_get_by_ids_with_documents_returns_empty_list_for_empty_input(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_project_repo.get_by_ids_with_documents([])

    assert result == []
    mock_session.execute.assert_not_called()


@pytest.mark.parametrize(
    "input_ids",
    [
        [1, 2, 3],
        [1, 1, 1],
    ],
    ids=["unique_ids", "duplicate_ids"],
)
async def test_get_by_ids_executes_query_and_returns_models(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
    input_ids: list[int],
) -> None:
    mock_result = MagicMock()
    expected_models = [Project(id=1, name="p1")]
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    result = await real_project_repo.get_by_ids(input_ids)

    assert result == expected_models
    mock_session.execute.assert_called_once()


async def test_get_by_ids_returns_empty_list_for_empty_input(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_project_repo.get_by_ids([])

    assert result == []
    mock_session.execute.assert_not_called()


async def test_get_all_applies_pagination_and_returns_models(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    expected_models = [Project(id=1, name="p1")]
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    result = await real_project_repo.get_all(skip=10, limit=5)

    assert result == expected_models
    mock_session.execute.assert_called_once()


async def test_get_by_id_returns_model_when_found(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    expected_model = Project(id=1, name="p1")
    mock_session.get.return_value = expected_model

    result = await real_project_repo.get_by_id(1)

    assert result is expected_model
    mock_session.get.assert_called_once_with(Project, 1)


async def test_get_by_id_returns_none_when_not_found(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.get.return_value = None

    result = await real_project_repo.get_by_id(999)

    assert result is None
    mock_session.get.assert_called_once_with(Project, 999)


async def test_create_adds_record_and_returns_model(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    create_data = ProjectCreateDBFactory.build()

    result = await real_project_repo.create(create_data)

    assert result.name == create_data.name
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.parametrize(
    ("constraint_name", "sqlstate", "expected_exception"),
    [
        ("pk_projects", PostgresErrorCode.UNIQUE_VIOLATION.value, UniqueFieldError),
        (
            "fk_projects_creator_id_users",
            PostgresErrorCode.FOREIGN_KEY_VIOLATION.value,
            RelatedObjectNotFoundError,
        ),
        (
            "ck_projects_check_project_name_min_len",
            PostgresErrorCode.CHECK_VIOLATION.value,
            CheckConstraintError,
        ),
    ],
    ids=["duplicate_pk", "fk_creator_id", "short_name"],
)
async def test_create_raises_mapped_exception_on_db_constraint_violation(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
    constraint_name: str,
    sqlstate: str,
    expected_exception: type[Exception],
) -> None:
    create_data = ProjectCreateDBFactory.build()

    orig = MagicMock()
    orig.sqlstate = sqlstate

    orig_cause = MagicMock()
    orig_cause.constraint_name = constraint_name
    orig_cause.table_name = "projects"

    orig.__cause__ = orig_cause

    mock_session.flush.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(expected_exception):
        await real_project_repo.create(create_data)


async def test_bulk_create_adds_multiple_records_and_returns_models(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    create_data_list = ProjectCreateDBFactory.batch(3)
    mock_result = MagicMock()
    expected_models = [Project(name=d.name) for d in create_data_list]
    mock_result.all.return_value = expected_models
    mock_session.scalars.return_value = mock_result

    result = await real_project_repo.bulk_create(create_data_list)

    assert result == expected_models
    mock_session.scalars.assert_called_once()


async def test_bulk_create_returns_empty_list_for_empty_input(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_project_repo.bulk_create([])

    assert result == []
    mock_session.scalars.assert_not_called()


async def test_bulk_create_raises_mapped_exception_on_integrity_error(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    create_data_list = ProjectCreateDBFactory.batch(2)

    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.FOREIGN_KEY_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "fk_projects_creator_id_users"
    orig_cause.table_name = "projects"

    orig.__cause__ = orig_cause

    mock_session.scalars.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(RelatedObjectNotFoundError):
        await real_project_repo.bulk_create(create_data_list)


async def test_bulk_update_modifies_multiple_records_and_returns_models(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = {1: ProjectUpdateDBFactory.build(), 2: ProjectUpdateDBFactory.build()}
    mock_result = MagicMock()
    expected_models = [Project(id=1), Project(id=2)]
    mock_result.all.return_value = expected_models
    mock_session.scalars.return_value = mock_result

    result = await real_project_repo.bulk_update(update_data)

    assert result == expected_models
    mock_session.execute.assert_called_once()
    mock_session.scalars.assert_called_once()


async def test_bulk_update_returns_empty_list_for_empty_input(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_project_repo.bulk_update({})

    assert result == []
    mock_session.execute.assert_not_called()


async def test_bulk_update_ignores_empty_update_schemas_and_returns_empty_list(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = {1: ProjectUpdateDB(), 2: ProjectUpdateDB()}

    result = await real_project_repo.bulk_update(update_data)

    assert result == []
    mock_session.execute.assert_not_called()


async def test_bulk_update_raises_mapped_exception_on_integrity_error(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = {1: ProjectUpdateDBFactory.build()}

    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.UNIQUE_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "pk_projects"
    orig_cause.table_name = "projects"

    orig.__cause__ = orig_cause

    mock_session.execute.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(UniqueFieldError):
        await real_project_repo.bulk_update(update_data)


async def test_update_modifies_existing_record_and_returns_model(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = ProjectUpdateDBFactory.build()
    mock_result = MagicMock()
    expected_model = Project(id=1, name=update_data.name)
    mock_result.scalar_one_or_none.return_value = expected_model
    mock_session.execute.return_value = mock_result

    result = await real_project_repo.update(1, update_data)

    assert result is expected_model
    mock_session.execute.assert_called_once()


async def test_update_returns_unmodified_record_if_empty_data(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    expected_model = Project(id=1, name="test")
    mock_session.get.return_value = expected_model

    result = await real_project_repo.update(1, ProjectUpdateDB())

    assert result is expected_model
    mock_session.get.assert_called_once_with(Project, 1)
    mock_session.execute.assert_not_called()


async def test_update_raises_mapped_exception_on_integrity_error(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = ProjectUpdateDBFactory.build()

    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.CHECK_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "ck_projects_check_project_name_min_len"
    orig_cause.table_name = "projects"

    orig.__cause__ = orig_cause

    mock_session.execute.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(CheckConstraintError):
        await real_project_repo.update(1, update_data)


@pytest.mark.parametrize(
    ("rowcount", "expected_result"),
    [
        (1, True),
        (0, False),
    ],
    ids=["record_deleted", "record_not_found"],
)
async def test_delete_removes_record_and_returns_bool(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
    rowcount: int,
    *,
    expected_result: bool,
) -> None:
    mock_result = MagicMock()
    mock_result.rowcount = rowcount
    mock_session.execute.return_value = mock_result

    result = await real_project_repo.delete(1)

    assert result is expected_result
    mock_session.execute.assert_called_once()


async def test_delete_raises_mapped_exception_on_integrity_error(
    real_project_repo: ProjectRepository,
    mock_session: AsyncMock,
) -> None:
    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.UNIQUE_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "pk_projects"
    orig_cause.table_name = "projects"

    orig.__cause__ = orig_cause

    mock_session.execute.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(UniqueFieldError):
        await real_project_repo.delete(1)
