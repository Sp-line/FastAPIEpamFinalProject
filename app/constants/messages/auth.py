# ruff: noqa: S105
from enum import StrEnum


class AuthErrorMessage(StrEnum):
    INVALID_CREDENTIALS = "Could not validate credentials."
    PASSWORD_TOO_WEAK = (
        "Password must contain at least one lowercase letter, "
        "one uppercase letter, and one number."
    )
