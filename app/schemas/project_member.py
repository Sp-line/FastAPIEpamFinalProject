from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import PositiveInt

from app.constants.role_type import RoleType
from app.schemas.base import Id


class ProjectMemberBase(BaseModel):
    role: RoleType = RoleType.PARTICIPANT


class ProjectMemberBaseWithRelations(ProjectMemberBase):
    user_id: PositiveInt
    project_id: PositiveInt


class ProjectMemberCreateReq(ProjectMemberBaseWithRelations):
    pass


class ProjectMemberCreateDB(ProjectMemberBaseWithRelations):
    pass


class ProjectMemberRead(Id, ProjectMemberBaseWithRelations):
    model_config = ConfigDict(from_attributes=True)


class ProjectMemberUpdateReq(BaseModel):
    role: RoleType


class ProjectMemberUpdateDB(BaseModel):
    user_id: PositiveInt | None = None
    project_id: PositiveInt | None = None

    role: RoleType | None = None
