from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.user import UserCreateDB
from app.schemas.user import UserCreateReq
from app.schemas.user import UserUpdateDB


class UserCreateReqFactory(ModelFactory[UserCreateReq]):
    __model__ = UserCreateReq

    @classmethod
    def password(cls) -> str:
        return "StrongPassword123!"


class UserCreateDBFactory(ModelFactory[UserCreateDB]):
    __model__ = UserCreateDB


class UserUpdateDBFactory(ModelFactory[UserUpdateDB]):
    __model__ = UserUpdateDB
