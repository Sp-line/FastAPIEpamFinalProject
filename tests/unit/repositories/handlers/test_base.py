from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.constants.db import PostgresErrorCode
from app.exceptions.db import DBError
from app.repositories.handlers.base import TableErrorHandler
from app.schemas.db import ConstraintRule


class DummyDBError(DBError):
    pass


def _create_mock_integrity_error(
    sqlstate: str | None = None,
    constraint_name: str | None = None,
    table_name: str | None = None,
) -> IntegrityError:
    cause = MagicMock()
    if constraint_name is not None:
        cause.constraint_name = constraint_name
    else:
        del cause.constraint_name

    if table_name is not None:
        cause.table_name = table_name
    else:
        del cause.table_name

    orig = MagicMock()
    if sqlstate is not None:
        orig.sqlstate = sqlstate
    else:
        del orig.sqlstate

    orig.__cause__ = cause

    return IntegrityError("INSERT INTO fake_table", {}, orig)


def test_parse_integrity_error_extracts_all_fields_correctly() -> None:
    exc = _create_mock_integrity_error(
        sqlstate="23505",
        constraint_name="uq_users_username",
        table_name="users",
    )

    result = TableErrorHandler._parse_integrity_error(exc)  # noqa: SLF001

    assert result.sqlstate == "23505"
    assert result.constraint_name == "uq_users_username"
    assert result.table_name == "users"


def test_parse_integrity_error_handles_missing_attributes() -> None:
    exc = _create_mock_integrity_error()

    result = TableErrorHandler._parse_integrity_error(exc)  # noqa: SLF001

    assert result.sqlstate == ""
    assert result.constraint_name == ""
    assert result.table_name == ""


def test_handle_raises_mapped_exception_when_rule_matches() -> None:
    rule = ConstraintRule(
        name="uq_users_username",
        error_code=PostgresErrorCode.UNIQUE_VIOLATION,
        exception=DummyDBError("Mapped rule exception triggered"),
    )
    handler = TableErrorHandler(rule)

    exc = _create_mock_integrity_error(
        sqlstate=PostgresErrorCode.UNIQUE_VIOLATION.value,
        constraint_name="uq_users_username",
    )

    with pytest.raises(DummyDBError, match="Mapped rule exception triggered"):
        handler.handle(exc)


def test_handle_does_nothing_when_rule_does_not_match() -> None:
    rule = ConstraintRule(
        name="uq_users_username",
        error_code=PostgresErrorCode.UNIQUE_VIOLATION,
        exception=DummyDBError(),
    )
    handler = TableErrorHandler(rule)

    exc = _create_mock_integrity_error(
        sqlstate=PostgresErrorCode.UNIQUE_VIOLATION.value,
        constraint_name="unknown_constraint",
    )

    handler.handle(exc)
