from pydantic import BaseModel
from pydantic import ConfigDict

from app.constants import PostgresErrorCode  # noqa: TC001
from app.exceptions.db import DBError  # noqa: TC001


class IntegrityErrorData(BaseModel):
    sqlstate: str
    constraint_name: str
    table_name: str


class ConstraintRule(BaseModel):
    name: str
    error_code: PostgresErrorCode
    exception: DBError

    model_config = ConfigDict(arbitrary_types_allowed=True)
