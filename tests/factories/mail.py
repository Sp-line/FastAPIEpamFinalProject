from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.mail import EmailMessage


class EmailMessageFactory(ModelFactory[EmailMessage]):
    __model__ = EmailMessage
