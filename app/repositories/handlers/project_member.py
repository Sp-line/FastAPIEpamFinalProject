from app.constants.db import PostgresErrorCode
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueError
from app.exceptions.db import UniqueFieldError
from app.repositories.handlers.base import TableErrorHandler
from app.schemas.db import ConstraintRule

pk_project_member_associations = ConstraintRule(
    name="pk_project_member_associations",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueFieldError(
        field_name="id",
        table_name="project_member_associations",
    ),
)

fk_project_member_associations_user_id_users = ConstraintRule(
    name="fk_project_member_associations_user_id_users",
    error_code=PostgresErrorCode.FOREIGN_KEY_VIOLATION,
    exception=RelatedObjectNotFoundError(
        field_name="user_id",
        table_name="project_member_associations",
    ),
)

fk_project_member_associations_project_id_projects = ConstraintRule(
    name="fk_project_member_associations_project_id_projects",
    error_code=PostgresErrorCode.FOREIGN_KEY_VIOLATION,
    exception=RelatedObjectNotFoundError(
        field_name="project_id",
        table_name="project_member_associations",
    ),
)

uq_user_project = ConstraintRule(
    name="uq_user_project",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueError(
        "project_member_associations",
        "user_id",
        "project_id",
    ),
)

ix_one_owner_per_project = ConstraintRule(
    name="ix_one_owner_per_project",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueFieldError(
        field_name="role",
        table_name="project_member_associations",
    ),
)

project_member_associations_error_handler = TableErrorHandler(
    pk_project_member_associations,
    fk_project_member_associations_user_id_users,
    fk_project_member_associations_project_id_projects,
    uq_user_project,
    ix_one_owner_per_project,
)
