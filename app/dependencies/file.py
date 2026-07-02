from typing import Annotated

from fastapi import File
from fastapi import UploadFile

from app.constants import DocumentMimeType
from app.constants.messages.file import FileErrorMessage
from app.exceptions.file import FileNameError
from app.exceptions.file import FileTypeError


def _check_document_file(file: UploadFile) -> None:
    if not file.filename:
        raise FileNameError(FileErrorMessage.FILENAME_MISSING)

    if not file.content_type or file.content_type not in DocumentMimeType:
        raise FileTypeError(
            file_type=file.content_type,
            allowed_types=list(DocumentMimeType),
        )


async def validate_document_file(
    file: Annotated[UploadFile, File(...)],
) -> UploadFile:
    _check_document_file(file)
    return file


async def validate_document_files(
    files: Annotated[list[UploadFile], File(...)],
) -> list[UploadFile]:
    for file in files:
        _check_document_file(file)
    return files
