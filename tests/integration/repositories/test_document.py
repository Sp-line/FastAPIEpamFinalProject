import uuid
from typing import TYPE_CHECKING

import pytest

from app.exceptions.db import CheckConstraintError
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueFieldError
from app.schemas.document import DocumentCreateDB
from app.schemas.document import DocumentUpdateDB
from tests.factories.document import DocumentCreateDBFactory
from tests.factories.project import ProjectCreateDBFactory
from tests.factories.user import UserCreateDBFactory

if TYPE_CHECKING:
    from app.repositories.document import DocumentRepository
    from app.repositories.project import ProjectRepository
    from app.repositories.user import UserRepository

pytestmark = pytest.mark.requires_db


def get_valid_s3_key() -> str:
    return str(uuid.uuid4())


async def test_create_inserts_record_in_db_and_returns_model(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    document_data = DocumentCreateDBFactory.build(
        project_id=project.id, s3_key=get_valid_s3_key()
    )

    created_document = await integration_document_repo.create(document_data)

    assert created_document.id is not None
    assert created_document.s3_key == document_data.s3_key
    assert created_document.project_id == project.id
    assert created_document.original_name == document_data.original_name


async def test_create_raises_related_object_not_found_error_on_invalid_project_id(
    integration_document_repo: DocumentRepository,
) -> None:
    document_data = DocumentCreateDBFactory.build(
        project_id=999999, s3_key=get_valid_s3_key()
    )

    with pytest.raises(RelatedObjectNotFoundError) as exc_info:
        await integration_document_repo.create(document_data)

    assert exc_info.value.field_name == "project_id"


async def test_create_raises_check_constraint_error_on_empty_original_name(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )

    document_data = DocumentCreateDB.model_construct(
        project_id=project.id,
        original_name="",
        s3_key=get_valid_s3_key(),
    )

    with pytest.raises(CheckConstraintError):
        await integration_document_repo.create(document_data)


async def test_create_raises_unique_field_error_on_duplicate_s3_key(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    shared_s3_key = get_valid_s3_key()

    doc_1 = DocumentCreateDBFactory.build(project_id=project.id, s3_key=shared_s3_key)
    doc_2 = DocumentCreateDBFactory.build(project_id=project.id, s3_key=shared_s3_key)

    await integration_document_repo.create(doc_1)

    with pytest.raises(UniqueFieldError) as exc_info:
        await integration_document_repo.create(doc_2)

    assert exc_info.value.field_name == "s3_key"


async def test_bulk_create_inserts_multiple_records(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    docs_data = [
        DocumentCreateDBFactory.build(project_id=project.id, s3_key=get_valid_s3_key()),
        DocumentCreateDBFactory.build(project_id=project.id, s3_key=get_valid_s3_key()),
    ]

    created_docs = await integration_document_repo.bulk_create(docs_data)

    assert len(created_docs) == 2  # noqa: PLR2004
    assert created_docs[0].id is not None
    assert created_docs[1].id is not None


async def test_bulk_update_modifies_multiple_records(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    docs = await integration_document_repo.bulk_create(
        [
            DocumentCreateDBFactory.build(
                project_id=project.id, s3_key=get_valid_s3_key()
            ),
            DocumentCreateDBFactory.build(
                project_id=project.id, s3_key=get_valid_s3_key()
            ),
        ]
    )

    update_mapping = {
        docs[0].id: DocumentUpdateDB(original_name="Updated Name 1"),
        docs[1].id: DocumentUpdateDB(original_name="Updated Name 2"),
    }

    updated_docs = await integration_document_repo.bulk_update(update_mapping)

    assert len(updated_docs) == 2  # noqa: PLR2004

    names = {doc.original_name for doc in updated_docs}
    assert "Updated Name 1" in names
    assert "Updated Name 2" in names


async def test_update_modifies_existing_record(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    doc = await integration_document_repo.create(
        DocumentCreateDBFactory.build(project_id=project.id, s3_key=get_valid_s3_key())
    )
    update_data = DocumentUpdateDB(original_name="New Valid Name")

    updated_doc = await integration_document_repo.update(doc.id, update_data)

    assert updated_doc is not None
    assert updated_doc.original_name == "New Valid Name"
    assert updated_doc.id == doc.id


async def test_delete_removes_record_from_db_and_returns_true(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    doc = await integration_document_repo.create(
        DocumentCreateDBFactory.build(project_id=project.id, s3_key=get_valid_s3_key())
    )

    is_deleted = await integration_document_repo.delete(doc.id)
    retrieved_doc = await integration_document_repo.get_by_id(doc.id)

    assert is_deleted is True
    assert retrieved_doc is None


async def test_delete_returns_false_if_record_does_not_exist(
    integration_document_repo: DocumentRepository,
) -> None:
    is_deleted = await integration_document_repo.delete(999999)

    assert is_deleted is False


async def test_get_by_id_returns_model_when_record_exists(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    doc = await integration_document_repo.create(
        DocumentCreateDBFactory.build(project_id=project.id, s3_key=get_valid_s3_key())
    )

    result = await integration_document_repo.get_by_id(doc.id)

    assert result is not None
    assert result.id == doc.id


async def test_get_by_ids_returns_correct_models(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    docs = await integration_document_repo.bulk_create(
        [
            DocumentCreateDBFactory.build(
                project_id=project.id, s3_key=get_valid_s3_key()
            ),
            DocumentCreateDBFactory.build(
                project_id=project.id, s3_key=get_valid_s3_key()
            ),
        ]
    )
    target_ids = [docs[0].id]

    results = await integration_document_repo.get_by_ids(target_ids)

    assert len(results) == 1
    assert results[0].id == docs[0].id


async def test_get_all_returns_all_models_with_pagination(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    await integration_document_repo.bulk_create(
        [
            DocumentCreateDBFactory.build(
                project_id=project.id, s3_key=get_valid_s3_key()
            ),
            DocumentCreateDBFactory.build(
                project_id=project.id, s3_key=get_valid_s3_key()
            ),
            DocumentCreateDBFactory.build(
                project_id=project.id, s3_key=get_valid_s3_key()
            ),
        ]
    )

    results = await integration_document_repo.get_all(skip=1, limit=2)

    assert len(results) == 2  # noqa: PLR2004


async def test_get_by_project_id_returns_only_documents_for_specified_project(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    proj_a = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    proj_b = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )

    await integration_document_repo.bulk_create(
        [
            DocumentCreateDBFactory.build(
                project_id=proj_a.id, s3_key=get_valid_s3_key()
            ),
            DocumentCreateDBFactory.build(
                project_id=proj_a.id, s3_key=get_valid_s3_key()
            ),
            DocumentCreateDBFactory.build(
                project_id=proj_b.id, s3_key=get_valid_s3_key()
            ),
        ]
    )

    results = await integration_document_repo.get_by_project_id(proj_a.id)

    assert len(results) == 2  # noqa: PLR2004
    assert all(doc.project_id == proj_a.id for doc in results)


async def test_get_keys_by_project_returns_list_of_keys(
    integration_document_repo: DocumentRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    proj = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )

    key1, key2 = get_valid_s3_key(), get_valid_s3_key()

    await integration_document_repo.bulk_create(
        [
            DocumentCreateDBFactory.build(project_id=proj.id, s3_key=key1),
            DocumentCreateDBFactory.build(project_id=proj.id, s3_key=key2),
        ]
    )

    keys = await integration_document_repo.get_keys_by_project(proj.id)

    assert len(keys) == 2  # noqa: PLR2004
    assert key1 in keys
    assert key2 in keys
