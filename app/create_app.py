from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_dishka
from fastapi import FastAPI

from app.dependencies import InfrastructureProvider
from app.dependencies import RepositoryProvider
from app.dependencies import ServiceProvider
from app.dependencies import UsagesProvider


def create() -> FastAPI:
    app = FastAPI()

    container = make_async_container(
        InfrastructureProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        UsagesProvider(),
    )

    setup_fastapi_dishka(container, app)

    return app
