from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.project import ProjectCreateDB
from app.schemas.project import ProjectCreateReq
from app.schemas.project import ProjectInfoReadWithDocuments
from app.schemas.project import ProjectInviteReq
from app.schemas.project import ProjectRead
from app.schemas.project import ProjectShareReq
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


class ProjectReadFactory(ModelFactory[ProjectRead]):
    __model__ = ProjectRead


class ProjectInviteReqFactory(ModelFactory[ProjectInviteReq]):
    __model__ = ProjectInviteReq


class ProjectShareReqFactory(ModelFactory[ProjectShareReq]):
    __model__ = ProjectShareReq
