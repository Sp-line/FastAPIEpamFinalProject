from typing import Any


class DBError(Exception):
    pass


class ObjectError(DBError):
    pass


class ObjectNotFoundError(ObjectError):
    def __init__(
        self,
        table_name: str,
        obj_id: int | None = None,
        conditions: dict[str, Any] | None = None,
    ) -> None:
        self.table_name = table_name
        self.obj_id = obj_id
        self.conditions = conditions

        if obj_id is not None:
            detail = f"id={obj_id}"
        elif conditions:
            detail = f"conditions={conditions}"
        else:
            detail = "specified parameters"

        super().__init__(f"Object with {detail} not found in table '{table_name}'")


class UniqueFieldError(DBError):
    def __init__(self, field_name: str, table_name: str) -> None:
        self.field_name = field_name
        self.table_name = table_name

        super().__init__(
            f"Obj with this '{field_name}' already exists in table '{table_name}'"
        )


class UniqueError(DBError):
    def __init__(self, table_name: str, *fields: str) -> None:
        self.table_name = table_name
        self.fields = fields

        fields_str = ", ".join(fields)
        super().__init__(
            f"Object with fields '{fields_str}' already exists in table '{table_name}'"
        )


class RelatedObjectNotFoundError(ObjectError):
    def __init__(self, field_name: str, table_name: str) -> None:
        self.field_name = field_name
        self.table_name = table_name

        super().__init__(
            f"Related object not found for field '{field_name}' in table '{table_name}'"
        )


class DeleteConstraintError(DBError):
    def __init__(self, table_name: str, referencing_table: str) -> None:
        self.table_name = table_name
        self.referencing_table = referencing_table

        super().__init__(
            f"Cannot delete object from table '{table_name}' "
            f"because it is referenced by "
            f"existing records in table '{referencing_table}'"
        )


class ExclusionError(DBError):
    def __init__(self, table_name: str, *fields: str) -> None:
        self.table_name = table_name
        self.fields = fields
        self.fields_str = ", ".join(fields)

        super().__init__(
            f"Conflicting or overlapping data detected for "
            f"fields '{self.fields_str}' in table '{table_name}'"
        )


class CheckConstraintError(DBError):
    def __init__(self, table_name: str, expression: str) -> None:
        self.table_name = table_name
        self.expression = expression

        super().__init__(
            f"Data validation failed in table '{table_name}'."
            f" Condition not met: '{expression}'"
        )
