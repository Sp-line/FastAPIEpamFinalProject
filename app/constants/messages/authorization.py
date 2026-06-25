from enum import StrEnum


class AuthorizationErrorMessage(StrEnum):
    PROJECT_DELETE_FORBIDDEN = "Only project owner can delete the project"
    PROJECT_UPDATE_FORBIDDEN = "Only project owner or participant can update the project"
