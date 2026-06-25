from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from pydantic import PositiveInt  # noqa: TC002

from app.core.config import settings
from app.dependencies.auth import get_current_user_id
from app.schemas.project import ProjectCreateReq  # noqa: TC001
from app.schemas.project import ProjectRead  # noqa: TC001
from app.usages.projects.create import ProjectCreateUsage  # noqa: TC001
from app.usages.projects.delete import ProjectDeleteUsage  # noqa: TC001

router = APIRouter(route_class=DishkaRoute, prefix=settings.api.v1.projects)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    data: ProjectCreateReq,
    project_create_usage: FromDishka[ProjectCreateUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> ProjectRead:
    return await project_create_usage(data, current_user_id)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: int,
    project_delete_usage: FromDishka[ProjectDeleteUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> None:
    await project_delete_usage(project_id, current_user_id)
