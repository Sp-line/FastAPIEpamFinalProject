from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_dishka
from fastapi import FastAPI

from app.constants.env_type import EnvironmentType
from app.core.config import settings
from app.dependencies import InfrastructureProvider
from app.dependencies import RepositoryProvider
from app.dependencies import ServiceProvider
from app.dependencies import UsagesProvider
from app.exceptions.handlers import register_exception_handlers


def create() -> FastAPI:
    app = FastAPI(
        docs_url="/docs" if settings.env != EnvironmentType.PROD else None,
        redoc_url="/redoc" if settings.env != EnvironmentType.PROD else None,
    )

    container = make_async_container(
        InfrastructureProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        UsagesProvider(),
    )

    setup_fastapi_dishka(container, app)
    register_exception_handlers(app)

    return app
