from enum import StrEnum


class EnvironmentType(StrEnum):
    LOCAL = "local"
    DEV = "development"
    STAGING = "staging"
    PROD = "production"
    TEST = "testing"
