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
from app.schemas.project import ProjectInfoReadWithDocuments  # noqa: TC001
from app.schemas.project import ProjectInviteReq  # noqa: TC001
from app.schemas.project import ProjectRead  # noqa: TC001
from app.schemas.project import ProjectUpdateReq  # noqa: TC001
from app.schemas.project_member import ProjectMemberRead  # noqa: TC001
from app.usages.projects.create import ProjectCreateUsage  # noqa: TC001
from app.usages.projects.delete import ProjectDeleteUsage  # noqa: TC001
from app.usages.projects.invite import ProjectInviteUsage  # noqa: TC001
from app.usages.projects.list import ProjectListInfoUsage  # noqa: TC001
from app.usages.projects.retrieve import ProjectRetrieveInfoUsage  # noqa: TC001
from app.usages.projects.update import ProjectUpdateUsage  # noqa: TC001

router = APIRouter(route_class=DishkaRoute, prefix=settings.api.v1.projects)


@router.post(
    "/{project_id}/invite",
    status_code=status.HTTP_201_CREATED,
)
async def invite_into_project(
    data: ProjectInviteReq,
    project_id: PositiveInt,
    project_invite_usage: FromDishka[ProjectInviteUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> ProjectMemberRead:
    return await project_invite_usage(project_id, data, current_user_id)


@router.post(
    "",
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
    project_id: PositiveInt,
    project_delete_usage: FromDishka[ProjectDeleteUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> None:
    await project_delete_usage(project_id, current_user_id)


@router.put(
    "/{project_id}/info",
)
async def update_project(
    project_id: PositiveInt,
    data: ProjectUpdateReq,
    project_update_usage: FromDishka[ProjectUpdateUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> ProjectRead:
    return await project_update_usage(project_id, data, current_user_id)


@router.get(
    "/{project_id}/info",
)
async def retrieve_project_info(
    project_id: PositiveInt,
    project_retrieve_info_usage: FromDishka[ProjectRetrieveInfoUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> ProjectRead:
    return await project_retrieve_info_usage(project_id, current_user_id)


@router.get(
    "",
)
async def list_project_info(
    project_list_info_usage: FromDishka[ProjectListInfoUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> list[ProjectInfoReadWithDocuments]:
    return await project_list_info_usage(current_user_id)
