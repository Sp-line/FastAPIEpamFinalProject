from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.project_member import ProjectMemberCreateDB
from app.schemas.project_member import ProjectMemberUpdateDB


class ProjectMemberCreateDBFactory(ModelFactory[ProjectMemberCreateDB]):
    __model__ = ProjectMemberCreateDB


class ProjectMemberUpdateDBFactory(ModelFactory[ProjectMemberUpdateDB]):
    __model__ = ProjectMemberUpdateDB
