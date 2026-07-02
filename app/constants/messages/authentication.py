# ruff: noqa: S105
from enum import StrEnum


class AuthenticationErrorMessage(StrEnum):
    INVALID_CREDENTIALS = "Could not validate credentials."
    PASSWORD_TOO_WEAK = (
        "Password must contain at least one lowercase letter, "
        "one uppercase letter, and one number."
    )
    TOKEN_EXPIRED = "Token has expired."
    TOKEN_INVALID = "Token is invalid or corrupted."
