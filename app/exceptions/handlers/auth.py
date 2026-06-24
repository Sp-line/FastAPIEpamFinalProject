from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from app.constants.messages.auth import AuthErrorMessage
from app.exceptions.auth import InvalidCredentialsError


async def invalid_credentials_handler(
    _: Request, __: InvalidCredentialsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": AuthErrorMessage.INVALID_CREDENTIALS.value},
        headers={"WWW-Authenticate": "Bearer"},
    )


def register_auth_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)  # type: ignore[arg-type]
