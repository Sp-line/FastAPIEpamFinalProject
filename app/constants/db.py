from enum import StrEnum
from enum import auto


class PostgresErrorCode(StrEnum):
    UNIQUE_VIOLATION = "23505"
    FOREIGN_KEY_VIOLATION = "23503"
    CHECK_VIOLATION = "23514"
    NOT_NULL_VIOLATION = "23502"
    RESTRICT_VIOLATION = "23001"
    EXCLUSION_VIOLATION = "23P01"


class DBDriver(StrEnum):
    ASYNCPG = auto()
    PSYCOPG = auto()
