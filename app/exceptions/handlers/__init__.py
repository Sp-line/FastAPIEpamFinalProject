from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

from app.exceptions.handlers.authentication import (
    register_authentication_exception_handlers,
)
from app.exceptions.handlers.authorization import (
    register_authorization_exception_handlers,
)
from app.exceptions.handlers.db import register_db_exception_handlers


def register_exception_handlers(app: FastAPI) -> None:
    register_db_exception_handlers(app)
    register_authentication_exception_handlers(app)
    register_authorization_exception_handlers(app)
