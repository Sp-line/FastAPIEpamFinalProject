from typing import Annotated

from dishka import FromDishka  # noqa: TC002
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TC002

from app.schemas.token import Token  # noqa: TC001
from app.schemas.user import UserCreateReq  # noqa: TC001
from app.schemas.user import UserRead  # noqa: TC001
from app.services.user import UserService  # noqa: TC001
from app.usages.users.login import UserLoginUsage  # noqa: TC001

router = APIRouter(route_class=DishkaRoute)


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def user_auth(
    data: UserCreateReq,
    service: FromDishka[UserService],
) -> UserRead:
    return await service.create(data)


@router.post("/login")
async def user_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_login_usage: FromDishka[UserLoginUsage],
) -> Token:
    return await user_login_usage(form_data)
