from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix=settings.api.prefix,
)
