from enum import StrEnum


class ConfigErrorMessage(StrEnum):
    LOCAL_S3_MISSING_CREDENTIALS = (
        "Local S3 requires endpoint_url, access_key, and secret_key to be provided."
    )
    LOCAL_SES_MISSING_CREDENTIALS = (
        "Local SES requires endpoint_url, access_key, and secret_key to be provided."
    )
