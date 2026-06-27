from fastapi import APIRouter

from app.api.api_v1.auth import router as auth_router
from app.api.api_v1.document import router as document_router
from app.api.api_v1.project import router as project_router
from app.core.config import settings

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(auth_router, tags=["User"])
router.include_router(project_router, tags=["Project"])
router.include_router(document_router, tags=["Document"])
