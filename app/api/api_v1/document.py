from typing import Annotated

from dishka import FromDishka  # noqa: TC002
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from fastapi import status
from pydantic import PositiveInt  # noqa: TC002

from app.dependencies.auth import get_current_user_id
from app.dependencies.file import validate_document_file
from app.dependencies.file import validate_document_files
from app.schemas.document import DocumentCreateReq
from app.schemas.document import DocumentDownload
from app.schemas.document import DocumentRead
from app.usages.documents.create import DocumentCreateUsage  # noqa: TC001
from app.usages.documents.delete import DocumentDeleteUsage  # noqa: TC001
from app.usages.documents.list import DocumentListUsage  # noqa: TC001
from app.usages.documents.retrieve import DocumentRetrieveUsage  # noqa: TC001
from app.usages.documents.update import DocumentUpdateUsage  # noqa: TC001

router = APIRouter(route_class=DishkaRoute)


@router.post(
    "/projects/{project_id}/documents",
    status_code=status.HTTP_201_CREATED,
)
async def create_documents(
    project_id: PositiveInt,
    files: Annotated[list[UploadFile], Depends(validate_document_files)],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
    document_create_usage: FromDishka[DocumentCreateUsage],
) -> list[DocumentRead]:
    data = DocumentCreateReq(project_id=project_id)
    return await document_create_usage(
        data=data,
        files=files,
        current_user_id=current_user_id,
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: PositiveInt,
    document_delete_usage: FromDishka[DocumentDeleteUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> None:
    await document_delete_usage(document_id, current_user_id)


@router.get(
    "/documents/{document_id}",
)
async def retrieve_document(
    document_id: PositiveInt,
    document_retrieve_usage: FromDishka[DocumentRetrieveUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> DocumentDownload:
    return await document_retrieve_usage(document_id, current_user_id)


@router.get(
    "/projects/{project_id}/documents",
)
async def list_documents(
    project_id: PositiveInt,
    document_list_usage: FromDishka[DocumentListUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> list[DocumentRead]:
    return await document_list_usage(project_id, current_user_id)


@router.put(
    "/documents/{document_id}",
)
async def update_document(
    document_id: PositiveInt,
    file: Annotated[UploadFile, Depends(validate_document_file)],
    document_update_usage: FromDishka[DocumentUpdateUsage],
    current_user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
) -> DocumentRead:
    return await document_update_usage(document_id, file, current_user_id)
