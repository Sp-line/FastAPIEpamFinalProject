from datetime import datetime  # noqa: TC003
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import PositiveInt

from app.constants.token import TokenType


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105


class JWTPayloadBase(BaseModel):
    sub: str
    exp: datetime | None = None
    type: TokenType


class JWTPayload(JWTPayloadBase):
    type: Literal[TokenType.ACCESS] = TokenType.ACCESS

    model_config = ConfigDict(from_attributes=True)


class InviteJWTPayload(JWTPayloadBase):
    type: Literal[TokenType.PROJECT_INVITE] = TokenType.PROJECT_INVITE

    project_id: PositiveInt

    model_config = ConfigDict(from_attributes=True)
