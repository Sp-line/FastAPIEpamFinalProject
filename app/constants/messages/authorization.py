from enum import StrEnum


class AuthorizationErrorMessage(StrEnum):
    FORBIDDEN = "You do not have permission to perform this action."
