from enum import StrEnum


class DocumentLimits:
    ORIGINAL_NAME_MAX: int = 255
    ORIGINAL_NAME_MIN: int = 1

    S3_KEY_MAX: int = 1024
    S3_KEY_MIN: int = 36


class DocumentMimeType(StrEnum):
    PDF = "application/pdf"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
