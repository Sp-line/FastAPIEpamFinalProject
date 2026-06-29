from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import SecretStr

from app.schemas.user import UserCreateDB
from app.schemas.user import UserCreateReq
from app.schemas.user import UserUpdateDB
from app.schemas.user import UserUpdateReq


class UserCreateReqFactory(ModelFactory[UserCreateReq]):
    __model__ = UserCreateReq

    @classmethod
    def password(cls) -> SecretStr:
        return SecretStr("StrongPassword123!")


class UserUpdateReqFactory(ModelFactory[UserUpdateReq]):
    __model__ = UserUpdateReq

    @classmethod
    def password(cls) -> SecretStr:
        return SecretStr("NewStrongPassword123!")


class UserCreateDBFactory(ModelFactory[UserCreateDB]):
    __model__ = UserCreateDB


class UserUpdateDBFactory(ModelFactory[UserUpdateDB]):
    __model__ = UserUpdateDB
