from enum import StrEnum


class MailErrorMessage(StrEnum):
    MISSING_CONTENT = (
        "Email content is missing: Please provide either 'body' or 'template_name'."
    )
