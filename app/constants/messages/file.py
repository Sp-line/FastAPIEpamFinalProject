from enum import StrEnum


class FileErrorMessage(StrEnum):
    FILENAME_MISSING = "File name is missing."
    INVALID_FILE_TYPE = "Invalid file type."
