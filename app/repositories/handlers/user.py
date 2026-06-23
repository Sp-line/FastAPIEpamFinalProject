from app.constants.db import PostgresErrorCode
from app.constants.user import UserLimits
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import UniqueFieldError
from app.repositories.handlers.base import TableErrorHandler
from app.schemas.db import ConstraintRule

pk_users = ConstraintRule(
    name="pk_users",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueFieldError(
        field_name="id",
        table_name="users",
    ),
)

uq_users_username = ConstraintRule(
    name="uq_users_username",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueFieldError(
        field_name="username",
        table_name="users",
    ),
)

check_user_username_min_len = ConstraintRule(
    name="check_user_username_min_len",
    error_code=PostgresErrorCode.CHECK_VIOLATION,
    exception=CheckConstraintError(
        table_name="users",
        expression=f"char_length(username) >= {UserLimits.USERNAME_MIN}",
    ),
)

check_user_hashed_password_min_len = ConstraintRule(
    name="check_user_hashed_password_min_len",
    error_code=PostgresErrorCode.CHECK_VIOLATION,
    exception=CheckConstraintError(
        table_name="users",
        expression=f"char_length(hashed_password) >= {UserLimits.HASHED_PASSWORD_MIN}",
    ),
)

users_error_handler = TableErrorHandler(
    pk_users,
    uq_users_username,
    check_user_username_min_len,
    check_user_hashed_password_min_len,
)
