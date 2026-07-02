# ruff: noqa: S106
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.constants.db import PostgresErrorCode
from app.core.models.user import User
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import UniqueFieldError

if TYPE_CHECKING:
    from app.repositories.user import UserRepository
from app.schemas.user import UserUpdateDB
from tests.factories.user import UserCreateDBFactory
from tests.factories.user import UserUpdateDBFactory


@pytest.mark.parametrize(
    ("constraint_name", "sqlstate", "expected_exception"),
    [
        (
            "uq_users_username",
            PostgresErrorCode.UNIQUE_VIOLATION.value,
            UniqueFieldError,
        ),
        (
            "ck_users_check_user_username_min_len",
            PostgresErrorCode.CHECK_VIOLATION.value,
            CheckConstraintError,
        ),
        (
            "ck_users_check_user_hashed_password_min_len",
            PostgresErrorCode.CHECK_VIOLATION.value,
            CheckConstraintError,
        ),
        ("pk_users", PostgresErrorCode.UNIQUE_VIOLATION.value, UniqueFieldError),
    ],
    ids=["duplicate_username", "short_username", "short_password", "duplicate_pk"],
)
async def test_create_raises_mapped_exception_on_db_constraint_violation(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
    constraint_name: str,
    sqlstate: str,
    expected_exception: type[Exception],
) -> None:
    create_data = UserCreateDBFactory.build()

    orig = MagicMock()
    orig.sqlstate = sqlstate

    orig_cause = MagicMock()
    orig_cause.constraint_name = constraint_name
    orig_cause.table_name = "users"

    orig.__cause__ = orig_cause

    mock_session.flush.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(expected_exception):
        await real_user_repo.create(create_data)


async def test_bulk_create_raises_mapped_exception_on_integrity_error(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    create_data_list = UserCreateDBFactory.batch(2)

    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.UNIQUE_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "uq_users_username"
    orig_cause.table_name = "users"

    orig.__cause__ = orig_cause

    mock_session.scalars.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(UniqueFieldError):
        await real_user_repo.bulk_create(create_data_list)


async def test_bulk_update_raises_mapped_exception_on_integrity_error(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = {1: UserUpdateDBFactory.build()}

    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.UNIQUE_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "uq_users_username"
    orig_cause.table_name = "users"

    orig.__cause__ = orig_cause

    mock_session.execute.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(UniqueFieldError):
        await real_user_repo.bulk_update(update_data)


async def test_update_raises_mapped_exception_on_integrity_error(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = UserUpdateDBFactory.build()

    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.UNIQUE_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "uq_users_username"
    orig_cause.table_name = "users"

    orig.__cause__ = orig_cause

    mock_session.execute.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(UniqueFieldError):
        await real_user_repo.update(1, update_data)


async def test_delete_raises_mapped_exception_on_integrity_error(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    orig = MagicMock()
    orig.sqlstate = PostgresErrorCode.UNIQUE_VIOLATION.value

    orig_cause = MagicMock()
    orig_cause.constraint_name = "uq_users_username"
    orig_cause.table_name = "users"

    orig.__cause__ = orig_cause

    mock_session.execute.side_effect = IntegrityError("stmt", "params", orig)

    with pytest.raises(UniqueFieldError):
        await real_user_repo.delete(1)


async def test_get_by_username_executes_query_and_returns_model(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    expected_model = User(id=1, username="test_user", hashed_password="pwd")
    mock_result.scalar_one_or_none.return_value = expected_model
    mock_session.execute.return_value = mock_result

    result = await real_user_repo.get_by_username("test_user")

    assert result is expected_model
    mock_session.execute.assert_called_once()


async def test_get_by_username_returns_none_if_no_record_found(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await real_user_repo.get_by_username("non_existent")

    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.parametrize(
    "input_ids",
    [
        [1, 2, 3],
        [1, 1, 1],
    ],
    ids=["unique_ids", "duplicate_ids"],
)
async def test_get_by_ids_executes_query_and_returns_models(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
    input_ids: list[int],
) -> None:
    mock_result = MagicMock()
    expected_models = [User(id=1, username="u1", hashed_password="p1")]
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    result = await real_user_repo.get_by_ids(input_ids)

    assert result == expected_models
    mock_session.execute.assert_called_once()


async def test_get_by_ids_returns_empty_list_for_empty_input(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_user_repo.get_by_ids([])

    assert result == []
    mock_session.execute.assert_not_called()


async def test_get_all_applies_pagination_and_returns_models(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    mock_result = MagicMock()
    expected_models = [User(id=1, username="u1", hashed_password="p1")]
    mock_result.scalars.return_value.all.return_value = expected_models
    mock_session.execute.return_value = mock_result

    result = await real_user_repo.get_all(skip=10, limit=5)

    assert result == expected_models
    mock_session.execute.assert_called_once()


async def test_get_by_id_returns_model_when_found(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    expected_model = User(id=1, username="test_user", hashed_password="pwd")
    mock_session.get.return_value = expected_model

    result = await real_user_repo.get_by_id(1)

    assert result is expected_model
    mock_session.get.assert_called_once_with(User, 1)


async def test_get_by_id_returns_none_when_not_found(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    mock_session.get.return_value = None

    result = await real_user_repo.get_by_id(999)

    assert result is None
    mock_session.get.assert_called_once_with(User, 999)


async def test_create_adds_record_and_returns_model(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    create_data = UserCreateDBFactory.build()

    result = await real_user_repo.create(create_data)

    assert result.username == create_data.username
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once()


async def test_bulk_create_adds_multiple_records_and_returns_models(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    create_data_list = UserCreateDBFactory.batch(3)
    mock_result = MagicMock()
    expected_models = [User(username=d.username) for d in create_data_list]
    mock_result.all.return_value = expected_models
    mock_session.scalars.return_value = mock_result

    result = await real_user_repo.bulk_create(create_data_list)

    assert result == expected_models
    mock_session.scalars.assert_called_once()


async def test_bulk_create_returns_empty_list_for_empty_input(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_user_repo.bulk_create([])

    assert result == []
    mock_session.scalars.assert_not_called()


async def test_bulk_update_modifies_multiple_records_and_returns_models(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = {1: UserUpdateDBFactory.build(), 2: UserUpdateDBFactory.build()}
    mock_result = MagicMock()
    expected_models = [User(id=1), User(id=2)]
    mock_result.all.return_value = expected_models
    mock_session.scalars.return_value = mock_result

    result = await real_user_repo.bulk_update(update_data)

    assert result == expected_models
    mock_session.execute.assert_called_once()
    mock_session.scalars.assert_called_once()


async def test_bulk_update_returns_empty_list_for_empty_input(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    result = await real_user_repo.bulk_update({})

    assert result == []
    mock_session.execute.assert_not_called()


async def test_bulk_update_ignores_empty_update_schemas_and_returns_empty_list(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = {1: UserUpdateDB(), 2: UserUpdateDB()}

    result = await real_user_repo.bulk_update(update_data)

    assert result == []
    mock_session.execute.assert_not_called()


async def test_update_modifies_existing_record_and_returns_model(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    update_data = UserUpdateDBFactory.build()
    mock_result = MagicMock()
    expected_model = User(id=1, username=update_data.username)
    mock_result.scalar_one_or_none.return_value = expected_model
    mock_session.execute.return_value = mock_result

    result = await real_user_repo.update(1, update_data)

    assert result is expected_model
    mock_session.execute.assert_called_once()


async def test_update_returns_unmodified_record_if_empty_data(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
) -> None:
    expected_model = User(id=1, username="test")
    mock_session.get.return_value = expected_model

    result = await real_user_repo.update(1, UserUpdateDB())

    assert result is expected_model
    mock_session.get.assert_called_once_with(User, 1)
    mock_session.execute.assert_not_called()


@pytest.mark.parametrize(
    ("rowcount", "expected_result"),
    [
        (1, True),
        (0, False),
    ],
    ids=["record_deleted", "record_not_found"],
)
async def test_delete_removes_record_and_returns_bool(
    real_user_repo: UserRepository,
    mock_session: AsyncMock,
    rowcount: int,
    *,
    expected_result: bool,
) -> None:
    mock_result = MagicMock()
    mock_result.rowcount = rowcount
    mock_session.execute.return_value = mock_result

    result = await real_user_repo.delete(1)

    assert result is expected_result
    mock_session.execute.assert_called_once()
