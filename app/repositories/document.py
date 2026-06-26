from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from app.core.models import Document
from app.repositories.base import RepositoryBase
from app.repositories.handlers.document import documents_error_handler
from app.schemas.document import DocumentCreateDB
from app.schemas.document import DocumentUpdateDB


class DocumentRepository(
    RepositoryBase[
        Document,
        DocumentCreateDB,
        DocumentUpdateDB,
    ]
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            model=Document,
            session=session,
            table_error_handler=documents_error_handler,
        )
