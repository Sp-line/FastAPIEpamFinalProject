from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import PropertyMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.constants.db import PostgresErrorCode
from app.constants.role_type import RoleType
from app.core.models.project_member import ProjectMemberAssociation
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueError
from app.exceptions.db import UniqueFieldError
from app.schemas.project_member import ProjectMemberUpdateDB
from tests.factories.project_member import ProjectMemberCreateDBFactory
from tests.factories.project_member import ProjectMemberUpdateDBFactory

if TYPE_CHECKING:
    from app.repositories.project_member import ProjectMemberAssociationRepository


async def test_get_by_user_and_project_executes_query_and_returns_model(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    expected_model = ProjectMemberAssociation(id=1, user_id=1, project_id=1)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_model
    mock_session.execute.return_value = mock_result

    result = await real_project_member_repo.get_by_user_and_project(
        user_id=1, project_id=1
    )

    assert result == expected_model
    mock_session.execute.assert_awaited_once()


async def test_get_project_ids_by_user_and_roles_returns_ids(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    expected_ids = [1, 2, 3]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_ids
    mock_session.execute.return_value = mock_result
    roles = {RoleType.OWNER, RoleType.PARTICIPANT}

    result = await real_project_member_repo.get_project_ids_by_user_and_roles(
        user_id=1, roles=roles
    )

    assert result == expected_ids
    mock_session.execute.assert_awaited_once()


async def test_get_project_ids_by_user_and_roles_returns_empty_list_if_roles_empty(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_project_member_repo.get_project_ids_by_user_and_roles(
        user_id=1, roles=set()
    )

    assert result == []
    mock_session.execute.assert_not_called()


async def test_create_persists_model_and_returns_it(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    member_data = ProjectMemberCreateDBFactory.build()

    result = await real_project_member_repo.create(member_data)

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
    assert result.user_id == member_data.user_id
    assert result.project_id == member_data.project_id


@pytest.mark.parametrize(
    ("error_code", "constraint_name", "expected_exception", "expected_field"),
    [
        (
            PostgresErrorCode.UNIQUE_VIOLATION,
            "pk_project_member_associations",
            UniqueFieldError,
            "id",
        ),
        (
            PostgresErrorCode.FOREIGN_KEY_VIOLATION,
            "fk_project_member_associations_user_id_users",
            RelatedObjectNotFoundError,
            "user_id",
        ),
        (
            PostgresErrorCode.FOREIGN_KEY_VIOLATION,
            "fk_project_member_associations_project_id_projects",
            RelatedObjectNotFoundError,
            "project_id",
        ),
        (PostgresErrorCode.UNIQUE_VIOLATION, "uq_user_project", UniqueError, None),
        (
            PostgresErrorCode.UNIQUE_VIOLATION,
            "ix_one_owner_per_project",
            UniqueFieldError,
            "role",
        ),
    ],
    ids=[
        "pk_project_member_associations",
        "fk_project_member_associations_user_id_users",
        "fk_project_member_associations_project_id_projects",
        "uq_user_project",
        "ix_one_owner_per_project",
    ],
)
async def test_create_raises_mapped_exception_on_integrity_error(  # noqa: PLR0913
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
    error_code: PostgresErrorCode,
    constraint_name: str,
    expected_exception: type[Exception],
    expected_field: str | None,
) -> None:
    member_data = ProjectMemberCreateDBFactory.build()

    orig = MagicMock()
    type(orig).sqlstate = PropertyMock(return_value=error_code.value)

    cause = MagicMock()
    type(cause).constraint_name = PropertyMock(return_value=constraint_name)

    orig.__cause__ = cause
    integrity_error = IntegrityError("statement", "params", orig)

    mock_session.flush.side_effect = integrity_error

    with pytest.raises(expected_exception) as exc_info:
        await real_project_member_repo.create(member_data)

    if expected_field and hasattr(exc_info.value, "field_name"):
        assert exc_info.value.field_name == expected_field


async def test_bulk_create_executes_query_and_returns_models(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    members_data = ProjectMemberCreateDBFactory.batch(2)
    expected_models = [ProjectMemberAssociation(id=1), ProjectMemberAssociation(id=2)]

    mock_result = MagicMock()
    mock_result.all.return_value = expected_models
    mock_session.scalars.return_value = mock_result

    results = await real_project_member_repo.bulk_create(members_data)

    assert results == expected_models
    mock_session.scalars.assert_awaited_once()


async def test_bulk_create_returns_empty_list_for_empty_input(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    results = await real_project_member_repo.bulk_create([])

    assert results == []
    mock_session.scalars.assert_not_called()


async def test_bulk_update_executes_query_and_returns_models(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    update_mapping = {
        1: ProjectMemberUpdateDBFactory.build(),
        2: ProjectMemberUpdateDBFactory.build(),
    }
    expected_models = [ProjectMemberAssociation(id=1), ProjectMemberAssociation(id=2)]

    mock_result = MagicMock()
    mock_result.all.return_value = expected_models
    mock_session.scalars.return_value = mock_result

    results = await real_project_member_repo.bulk_update(update_mapping)

    assert results == expected_models
    mock_session.execute.assert_awaited_once()
    mock_session.scalars.assert_awaited_once()


async def test_bulk_update_returns_empty_list_for_empty_input(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    results = await real_project_member_repo.bulk_update({})

    assert results == []
    mock_session.execute.assert_not_called()


async def test_update_executes_query_and_returns_model(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = ProjectMemberUpdateDBFactory.build()
    expected_model = ProjectMemberAssociation(id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_model
    mock_session.execute.return_value = mock_result

    result = await real_project_member_repo.update(1, update_data)

    assert result == expected_model
    mock_session.execute.assert_awaited_once()


async def test_update_returns_get_if_data_is_empty(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    empty_update_data = ProjectMemberUpdateDB()

    expected_model = ProjectMemberAssociation(id=1)
    mock_session.get.return_value = expected_model

    result = await real_project_member_repo.update(1, empty_update_data)

    assert result == expected_model
    mock_session.get.assert_awaited_once()
    mock_session.execute.assert_not_called()


async def test_delete_executes_query_and_returns_true(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_session.execute.return_value = mock_result

    result = await real_project_member_repo.delete(1)

    assert result is True
    mock_session.execute.assert_awaited_once()


async def test_delete_returns_false_when_no_rows_affected(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_session.execute.return_value = mock_result

    result = await real_project_member_repo.delete(1)

    assert result is False
    mock_session.execute.assert_awaited_once()


async def test_get_by_id_returns_model(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    expected_model = ProjectMemberAssociation(id=1)
    mock_session.get.return_value = expected_model

    result = await real_project_member_repo.get_by_id(1)

    assert result == expected_model
    mock_session.get.assert_awaited_once()


async def test_get_by_ids_returns_models(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    expected_models = [ProjectMemberAssociation(id=1), ProjectMemberAssociation(id=2)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    results = await real_project_member_repo.get_by_ids([1, 2])

    assert results == expected_models
    mock_session.execute.assert_awaited_once()


async def test_get_by_ids_returns_empty_list_for_empty_input(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    results = await real_project_member_repo.get_by_ids([])

    assert results == []
    mock_session.execute.assert_not_called()


async def test_get_all_returns_models_with_pagination(
    real_project_member_repo: ProjectMemberAssociationRepository,
    mock_session: AsyncMock,
) -> None:
    expected_models = [ProjectMemberAssociation(id=1), ProjectMemberAssociation(id=2)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    results = await real_project_member_repo.get_all(skip=10, limit=5)

    assert results == expected_models
    mock_session.execute.assert_awaited_once()
