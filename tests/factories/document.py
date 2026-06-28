from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.document import DocumentCreateDB


class DocumentCreateDBFactory(ModelFactory[DocumentCreateDB]):
    __model__ = DocumentCreateDB
