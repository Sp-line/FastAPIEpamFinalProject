from typing import Annotated

from annotated_types import MaxLen
from annotated_types import MinLen
from pydantic import AfterValidator
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import SecretStr

from app.constants.user import UserLimits
from app.schemas.base import Id
from app.utils.password_validator import validate_password_strength

type PasswordStr = Annotated[
    SecretStr,
    Field(min_length=UserLimits.PASSWORD_MIN, max_length=UserLimits.PASSWORD_MAX),
    AfterValidator(validate_password_strength),
]
type Username = Annotated[
    str, MinLen(UserLimits.USERNAME_MIN), MaxLen(UserLimits.USERNAME_MAX)
]
type HashedPassword = Annotated[
    str,
    MinLen(UserLimits.HASHED_PASSWORD_MIN),
    MaxLen(UserLimits.HASHED_PASSWORD_MAX),
]


class UserBase(BaseModel):
    username: Username


class UserCreateReq(UserBase):
    password: PasswordStr


class UserCreateDB(UserBase):
    hashed_password: HashedPassword


class UserRead(UserBase, Id):
    model_config = ConfigDict(from_attributes=True)


class UserUpdateBase(BaseModel):
    username: Username | None = None


class UserUpdateReq(UserUpdateBase):
    password: PasswordStr | None = None


class UserUpdateDB(UserUpdateBase):
    hashed_password: HashedPassword | None = None
