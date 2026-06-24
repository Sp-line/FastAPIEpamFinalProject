from typing import Annotated

from dishka.integrations.fastapi import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import PositiveInt  # noqa: TC002

from app.core.auth.jwt import JWTService  # noqa: TC001

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def extract_user_id_from_token(token: str, jwt_service: JWTService) -> PositiveInt:
    payload = jwt_service.verify_access_token(token)
    return int(payload.sub)


@inject
def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_service: FromDishka[JWTService],
) -> PositiveInt:
    return extract_user_id_from_token(token, jwt_service)
