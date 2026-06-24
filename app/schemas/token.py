from datetime import datetime  # noqa: TC003
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105


class JWTPayload(BaseModel):
    sub: str
    exp: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
