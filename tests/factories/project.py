from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.project import ProjectCreateDB
from app.schemas.project import ProjectCreateReq
from app.schemas.project import ProjectInfoReadWithDocuments
from app.schemas.project import ProjectUpdateDB
from app.schemas.project import ProjectUpdateReq


class ProjectCreateReqFactory(ModelFactory[ProjectCreateReq]):
    __model__ = ProjectCreateReq


class ProjectUpdateReqFactory(ModelFactory[ProjectUpdateReq]):
    __model__ = ProjectUpdateReq


class ProjectCreateDBFactory(ModelFactory[ProjectCreateDB]):
    __model__ = ProjectCreateDB


class ProjectUpdateDBFactory(ModelFactory[ProjectUpdateDB]):
    __model__ = ProjectUpdateDB


class ProjectInfoReadWithDocumentsFactory(ModelFactory[ProjectInfoReadWithDocuments]):
    __model__ = ProjectInfoReadWithDocuments
