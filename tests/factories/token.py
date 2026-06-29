from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.token import JWTPayload


class JWTPayloadFactory(ModelFactory[JWTPayload]):
    __model__ = JWTPayload
