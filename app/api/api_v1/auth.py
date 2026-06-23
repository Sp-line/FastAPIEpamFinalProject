from dishka import FromDishka  # noqa: TC002
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi import status

from app.schemas.user import UserCreateReq  # noqa: TC001
from app.schemas.user import UserRead  # noqa: TC001
from app.services.user import UserService  # noqa: TC001

router = APIRouter(route_class=DishkaRoute)


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def user_auth(
    data: UserCreateReq,
    service: FromDishka[UserService],
) -> UserRead:
    return await service.create(data)
