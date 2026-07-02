from abc import ABC
from abc import abstractmethod
from uuid import uuid4

from slugify import slugify

from app.schemas.storage import DocumentKeyBuild
from app.schemas.storage import KeyBuild


class S3KeyStrategy[TKeyBuild: KeyBuild](ABC):
    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    @abstractmethod
    def generate(self, data: TKeyBuild) -> str: ...


class DocumentKeyStrategy(S3KeyStrategy[DocumentKeyBuild]):
    def __init__(self) -> None:
        super().__init__(
            prefix="documents",
        )

    def generate(self, data: DocumentKeyBuild) -> str:
        name_slug = slugify(data.original_name, max_length=50, separator="_")
        unique_id = str(uuid4())

        return f"{self._prefix}/{data.project_id}/{name_slug}_{unique_id}"
