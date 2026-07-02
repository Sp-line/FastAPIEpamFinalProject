from typing import Annotated

from annotated_types import MaxLen
from annotated_types import MinLen
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import HttpUrl
from pydantic import PositiveInt

from app.constants.document import DocumentLimits
from app.schemas.base import Id

type OriginalName = Annotated[
    str,
    MinLen(DocumentLimits.ORIGINAL_NAME_MIN),
    MaxLen(DocumentLimits.ORIGINAL_NAME_MAX),
]
type S3Key = Annotated[
    str, MinLen(DocumentLimits.S3_KEY_MIN), MaxLen(DocumentLimits.S3_KEY_MAX)
]


class DocumentBase(BaseModel):
    pass


class DocumentBaseWithRelations(DocumentBase):
    project_id: PositiveInt


class DocumentCreateReq(DocumentBaseWithRelations):
    pass


class DocumentCreateDB(DocumentBaseWithRelations):
    original_name: OriginalName
    s3_key: S3Key


class DocumentUpdateBase(BaseModel):
    pass


class DocumentUpdateReq(DocumentUpdateBase):
    pass


class DocumentUpdateDB(DocumentUpdateBase):
    project_id: PositiveInt | None = None
    original_name: OriginalName | None = None
    s3_key: S3Key | None = None


class DocumentRead(Id, DocumentBaseWithRelations):
    original_name: OriginalName

    model_config = ConfigDict(from_attributes=True)


class DocumentDownload(DocumentRead):
    download_url: HttpUrl

    model_config = ConfigDict(from_attributes=True)
