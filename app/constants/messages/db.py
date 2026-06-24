from enum import StrEnum


class DBErrorMessage(StrEnum):
    NOT_FOUND = "Requested resource not found."
    UNIQUE_FIELD = "Resource with this {field_name} already exists."
    UNIQUE_MULTIPLE = "Resource with these fields already exists: {fields}."
    RELATED_NOT_FOUND = "Related resource for field '{field_name}' not found."
    DELETE_CONSTRAINT = (
        "Cannot delete this resource because it is in use by other records."
    )
    EXCLUSION_CONSTRAINT = "Operation conflicts with existing business rules."
    CHECK_CONSTRAINT = "Provided data violates validation rules."
    INTEGRITY_ERROR = "A database integrity conflict occurred."
