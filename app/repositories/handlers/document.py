from app.constants.db import PostgresErrorCode
from app.constants.document import DocumentLimits
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueFieldError
from app.repositories.handlers.base import TableErrorHandler
from app.schemas.db import ConstraintRule

pk_documents = ConstraintRule(
    name="pk_documents",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueFieldError(
        field_name="id",
        table_name="documents",
    ),
)

uq_documents_s3_key = ConstraintRule(
    name="uq_documents_s3_key",
    error_code=PostgresErrorCode.UNIQUE_VIOLATION,
    exception=UniqueFieldError(
        field_name="s3_key",
        table_name="documents",
    ),
)

fk_documents_project_id_projects = ConstraintRule(
    name="fk_documents_project_id_projects",
    error_code=PostgresErrorCode.FOREIGN_KEY_VIOLATION,
    exception=RelatedObjectNotFoundError(
        field_name="project_id",
        table_name="projects",
    ),
)

check_document_original_name_min_len = ConstraintRule(
    name="ck_documents_check_document_original_name_min_len",
    error_code=PostgresErrorCode.CHECK_VIOLATION,
    exception=CheckConstraintError(
        table_name="documents",
        expression=f"char_length(original_name) >= {DocumentLimits.ORIGINAL_NAME_MIN}",
    ),
)

check_document_s3_key_min_len = ConstraintRule(
    name="ck_documents_check_document_s3_key_min_len",
    error_code=PostgresErrorCode.CHECK_VIOLATION,
    exception=CheckConstraintError(
        table_name="documents",
        expression=f"char_length(s3_key) >= {DocumentLimits.S3_KEY_MIN}",
    ),
)

documents_error_handler = TableErrorHandler(
    pk_documents,
    uq_documents_s3_key,
    fk_documents_project_id_projects,
    check_document_original_name_min_len,
    check_document_s3_key_min_len,
)
