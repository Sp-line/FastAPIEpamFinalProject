from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.project import ProjectCreateReq
from app.schemas.project import ProjectUpdateReq


class ProjectCreateReqFactory(ModelFactory[ProjectCreateReq]):
    __model__ = ProjectCreateReq


class ProjectUpdateReqFactory(ModelFactory[ProjectUpdateReq]):
    __model__ = ProjectUpdateReq
