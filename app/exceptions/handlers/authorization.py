from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.exceptions.authorization import ForbiddenError


async def forbidden_error_handler(
    _: Request,
    __: ForbiddenError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": AuthorizationErrorMessage.FORBIDDEN},
    )


def register_authorization_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ForbiddenError, forbidden_error_handler)  # type: ignore[arg-type]
