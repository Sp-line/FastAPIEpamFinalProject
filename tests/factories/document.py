from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.document import DocumentCreateDB
from app.schemas.document import DocumentUpdateDB
from app.schemas.storage import DocumentKeyBuild


class DocumentCreateDBFactory(ModelFactory[DocumentCreateDB]):
    __model__ = DocumentCreateDB


class DocumentUpdateDBFactory(ModelFactory[DocumentUpdateDB]):
    __model__ = DocumentUpdateDB


class DocumentKeyBuildFactory(ModelFactory[DocumentKeyBuild]):
    __model__ = DocumentKeyBuild
