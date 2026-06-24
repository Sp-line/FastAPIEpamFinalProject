from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.constants.messages.db import DBErrorMessage
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import DeleteConstraintError
from app.exceptions.db import ExclusionError
from app.exceptions.db import ObjectNotFoundError
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueError
from app.exceptions.db import UniqueFieldError


async def object_not_found_handler(_: Request, __: ObjectNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": DBErrorMessage.NOT_FOUND},
    )


async def unique_field_handler(_: Request, exc: UniqueFieldError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": DBErrorMessage.UNIQUE_FIELD.format(field_name=exc.field_name)
        },
    )


async def unique_handler(_: Request, exc: UniqueError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": DBErrorMessage.UNIQUE_MULTIPLE.format(fields=", ".join(exc.fields))
        },
    )


async def related_object_not_found_handler(
    _: Request, exc: RelatedObjectNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": DBErrorMessage.RELATED_NOT_FOUND.format(field_name=exc.field_name)
        },
    )


async def delete_constraint_handler(
    _: Request, __: DeleteConstraintError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": DBErrorMessage.DELETE_CONSTRAINT},
    )


async def exclusion_constraint_handler(_: Request, __: ExclusionError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": DBErrorMessage.EXCLUSION_CONSTRAINT},
    )


async def check_constraint_handler(_: Request, __: CheckConstraintError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": DBErrorMessage.CHECK_CONSTRAINT},
    )


async def integrity_error_handler(_: Request, __: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": DBErrorMessage.INTEGRITY_ERROR},
    )


def register_db_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ObjectNotFoundError, object_not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(UniqueFieldError, unique_field_handler)  # type: ignore[arg-type]
    app.add_exception_handler(UniqueError, unique_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RelatedObjectNotFoundError,
        related_object_not_found_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(DeleteConstraintError, delete_constraint_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ExclusionError, exclusion_constraint_handler)  # type: ignore[arg-type]
    app.add_exception_handler(CheckConstraintError, check_constraint_handler)  # type: ignore[arg-type]
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # type: ignore[arg-type]
