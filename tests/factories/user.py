from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.user import UserCreateReq


class UserCreateReqFactory(ModelFactory[UserCreateReq]):
    __model__ = UserCreateReq

    @classmethod
    def password(cls) -> str:
        return "StrongPassword123!"
