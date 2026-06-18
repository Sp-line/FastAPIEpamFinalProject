from dependencies import InfrastructureProvider
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_dishka
from fastapi import FastAPI


def create() -> FastAPI:
    app = FastAPI()

    container = make_async_container(
        InfrastructureProvider(),
    )

    setup_fastapi_dishka(container, app)

    return app
