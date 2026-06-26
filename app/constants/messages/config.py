from enum import StrEnum


class ConfigErrorMessage(StrEnum):
    LOCAL_S3_MISSING_CREDENTIALS = (
        "Local MinIO requires endpoint_url, access_key, and secret_key to be provided."
    )
