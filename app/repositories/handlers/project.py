from app.constants.db import PostgresErrorCode
from app.constants.project import ProjectLimits
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueFieldError
from app.repositories.handlers.base import TableErrorHandler
from app.schemas.db import ConstraintRule

pk_projects = ConstraintRule(
    name="pk_projects",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueFieldError(
        field_name="id",
        table_name="projects",
    ),
)

fk_projects_creator_id_users = ConstraintRule(
    name="fk_projects_creator_id_users",
    error_code=PostgresErrorCode.FOREIGN_KEY_VIOLATION,
    exception=RelatedObjectNotFoundError(
        field_name="creator_id",
        table_name="projects",
    ),
)

check_project_name_min_len = ConstraintRule(
    name="ck_projects_check_project_name_min_len",
    error_code=PostgresErrorCode.CHECK_VIOLATION,
    exception=CheckConstraintError(
        table_name="projects",
        expression=f"char_length(name) >= {ProjectLimits.NAME_MIN}",
    ),
)

projects_error_handler = TableErrorHandler(
    pk_projects,
    fk_projects_creator_id_users,
    check_project_name_min_len,
)
