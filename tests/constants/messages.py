from enum import StrEnum


class Messages(StrEnum):
    SKIP_DB_INITIALIZATION = "No tests require database - skipping Postgres container"
