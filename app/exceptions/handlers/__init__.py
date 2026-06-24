from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

from app.exceptions.handlers.auth import register_auth_exception_handlers
from app.exceptions.handlers.db import register_db_exception_handlers


def register_exception_handlers(app: FastAPI) -> None:
    register_db_exception_handlers(app)
    register_auth_exception_handlers(app)
