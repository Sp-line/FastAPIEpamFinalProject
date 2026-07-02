from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from app.constants.messages.file import FileErrorMessage
from app.exceptions.file import FileNameError
from app.exceptions.file import FileTypeError


async def file_name_error_handler(
    _: Request,
    __: FileNameError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": FileErrorMessage.FILENAME_MISSING},
    )


async def file_type_error_handler(
    _: Request,
    __: FileTypeError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": FileErrorMessage.INVALID_FILE_TYPE},
    )


def register_file_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(FileNameError, file_name_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(FileTypeError, file_type_error_handler)  # type: ignore[arg-type]
