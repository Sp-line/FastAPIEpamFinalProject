from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from app.constants.messages.auth import AuthErrorMessage
from app.exceptions.authentication import InvalidCredentialsError
from app.exceptions.authentication import TokenExpiredError
from app.exceptions.authentication import TokenInvalidError


async def invalid_credentials_handler(
    _: Request, __: InvalidCredentialsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": AuthErrorMessage.INVALID_CREDENTIALS},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def token_expired_handler(_: Request, __: TokenExpiredError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": AuthErrorMessage.TOKEN_EXPIRED},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def token_invalid_handler(_: Request, __: TokenInvalidError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": AuthErrorMessage.TOKEN_INVALID},
        headers={"WWW-Authenticate": "Bearer"},
    )


def register_auth_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)  # type: ignore[arg-type]
    app.add_exception_handler(TokenExpiredError, token_expired_handler)  # type: ignore[arg-type]
    app.add_exception_handler(TokenInvalidError, token_invalid_handler)  # type: ignore[arg-type]
