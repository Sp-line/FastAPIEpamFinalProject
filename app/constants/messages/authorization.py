from enum import StrEnum


class AuthorizationErrorMessage(StrEnum):
    PROJECT_DELETE_FORBIDDEN = "Only project owner can delete the project"
