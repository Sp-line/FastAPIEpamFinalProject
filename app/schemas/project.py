from typing import Annotated

from annotated_types import MaxLen
from annotated_types import MinLen
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import PositiveInt

from app.constants.project import ProjectLimits
from app.schemas.base import Id

type ProjectName = Annotated[
    str, MinLen(ProjectLimits.NAME_MIN), MaxLen(ProjectLimits.NAME_MAX)
]


class ProjectBase(BaseModel):
    name: ProjectName
    description: str | None = None


class ProjectCreateReq(ProjectBase):
    pass


class ProjectCreateDB(ProjectBase):
    creator_id: PositiveInt


class ProjectUpdateReq(BaseModel):
    name: ProjectName
    description: str | None


class ProjectUpdateDB(BaseModel):
    name: ProjectName | None = None
    description: str | None = None

    creator_id: PositiveInt | None = None


class ProjectRead(Id, ProjectBase):
    creator_id: PositiveInt

    model_config = ConfigDict(from_attributes=True)
