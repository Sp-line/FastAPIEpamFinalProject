import uvicorn

from app.api import router
from app.core.config import settings
from app.create_app import create

app = create()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
