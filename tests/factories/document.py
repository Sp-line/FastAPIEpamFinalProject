from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.document import DocumentCreateDB
from app.schemas.document import DocumentUpdateDB


class DocumentCreateDBFactory(ModelFactory[DocumentCreateDB]):
    __model__ = DocumentCreateDB


class DocumentUpdateDBFactory(ModelFactory[DocumentUpdateDB]):
    __model__ = DocumentUpdateDB
