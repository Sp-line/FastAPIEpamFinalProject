from pydantic import BaseModel
from pydantic import PositiveInt


class KeyBuild(BaseModel):
    original_name: str


class DocumentKeyBuild(KeyBuild):
    project_id: PositiveInt
