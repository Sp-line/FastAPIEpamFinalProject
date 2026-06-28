from enum import StrEnum


class ConfigErrorMessage(StrEnum):
    LOCAL_S3_MISSING_CREDENTIALS = (
        "Local MinIO requires endpoint_url, access_key, and secret_key to be provided."
    )
    MISSING_LOCAL_EMAIL_CONFIG = "Missing FastAPI Mail config for local/test env."
    MISSING_PROD_EMAIL_CONFIG = "Missing AWS SES config for production env."
    UNSUPPORTED_ENVIRONMENT = "Unsupported environment: {env}"
