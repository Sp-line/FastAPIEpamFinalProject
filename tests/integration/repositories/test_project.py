from typing import TYPE_CHECKING

import pytest

from app.exceptions.db import CheckConstraintError
from app.exceptions.db import RelatedObjectNotFoundError
from app.schemas.project import ProjectCreateDB
from app.schemas.project import ProjectUpdateDB
from tests.factories.document import DocumentCreateDBFactory
from tests.factories.project import ProjectCreateDBFactory
from tests.factories.user import UserCreateDBFactory

if TYPE_CHECKING:
    from app.repositories.document import DocumentRepository
    from app.repositories.project import ProjectRepository
    from app.repositories.user import UserRepository

pytestmark = pytest.mark.requires_db


async def test_create_inserts_record_in_db_and_returns_model(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    project_data = ProjectCreateDBFactory.build(creator_id=created_user.id)

    created_project = await integration_project_repo.create(project_data)

    assert created_project.id is not None
    assert created_project.name == project_data.name
    assert created_project.creator_id == created_user.id


async def test_create_raises_related_object_not_found_error_on_missing_creator(
    integration_project_repo: ProjectRepository,
) -> None:
    project_data = ProjectCreateDBFactory.build(creator_id=999999)

    with pytest.raises(RelatedObjectNotFoundError) as exc_info:
        await integration_project_repo.create(project_data)

    assert exc_info.value.field_name == "creator_id"
    assert exc_info.value.table_name == "projects"


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "A",
    ],
    ids=["empty_string", "single_character"],
)
async def test_create_raises_check_constraint_error_on_invalid_name_length(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
    invalid_name: str,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)

    project_data = ProjectCreateDB.model_construct(
        name=invalid_name,
        description="test description",
        creator_id=created_user.id,
    )

    with pytest.raises(CheckConstraintError) as exc_info:
        await integration_project_repo.create(project_data)

    assert exc_info.value.table_name == "projects"
    assert "char_length(name) >=" in exc_info.value.expression


async def test_bulk_create_inserts_multiple_records_and_returns_models(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    projects_data = ProjectCreateDBFactory.batch(3, creator_id=created_user.id)

    created_projects = await integration_project_repo.bulk_create(projects_data)

    assert len(created_projects) == 3  # noqa: PLR2004
    for idx, project in enumerate(created_projects):
        assert project.id is not None
        assert project.name == projects_data[idx].name
        assert project.creator_id == created_user.id


async def test_get_by_id_returns_model_when_record_exists(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    project_data = ProjectCreateDBFactory.build(creator_id=created_user.id)
    created_project = await integration_project_repo.create(project_data)

    result = await integration_project_repo.get_by_id(created_project.id)

    assert result is not None
    assert result.id == created_project.id


async def test_get_by_id_returns_none_when_record_does_not_exist(
    integration_project_repo: ProjectRepository,
) -> None:
    result = await integration_project_repo.get_by_id(999999)

    assert result is None


async def test_get_by_ids_returns_models_for_existing_records(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    projects_data = ProjectCreateDBFactory.batch(3, creator_id=created_user.id)
    created_projects = await integration_project_repo.bulk_create(projects_data)
    target_ids = [created_projects[0].id, created_projects[2].id]

    results = await integration_project_repo.get_by_ids(target_ids)

    assert len(results) == 2  # noqa: PLR2004
    returned_ids = {p.id for p in results}
    assert set(target_ids) == returned_ids


async def test_get_all_returns_paginated_models(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    projects_data = ProjectCreateDBFactory.batch(5, creator_id=created_user.id)
    await integration_project_repo.bulk_create(projects_data)

    results_first_page = await integration_project_repo.get_all(skip=0, limit=2)
    results_second_page = await integration_project_repo.get_all(skip=2, limit=2)

    assert len(results_first_page) == 2  # noqa: PLR2004
    assert len(results_second_page) == 2  # noqa: PLR2004
    assert results_first_page[0].id != results_second_page[0].id


async def test_update_modifies_existing_record_and_returns_model(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    project_data = ProjectCreateDBFactory.build(creator_id=created_user.id)
    created_project = await integration_project_repo.create(project_data)

    update_data = ProjectUpdateDB(
        name="Updated Project Name",
        description="Updated Description",
    )

    updated_project = await integration_project_repo.update(
        created_project.id,
        update_data,
    )

    assert updated_project is not None
    assert updated_project.id == created_project.id
    assert updated_project.name == update_data.name
    assert updated_project.description == update_data.description


async def test_update_returns_none_when_record_does_not_exist(
    integration_project_repo: ProjectRepository,
) -> None:
    update_data = ProjectUpdateDB(name="Updated Project Name")

    result = await integration_project_repo.update(999999, update_data)

    assert result is None


async def test_delete_removes_record_and_returns_true(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    project_data = ProjectCreateDBFactory.build(creator_id=created_user.id)
    created_project = await integration_project_repo.create(project_data)

    result = await integration_project_repo.delete(created_project.id)
    retrieved_project = await integration_project_repo.get_by_id(created_project.id)

    assert result is True
    assert retrieved_project is None


async def test_delete_returns_false_when_record_does_not_exist(
    integration_project_repo: ProjectRepository,
) -> None:
    result = await integration_project_repo.delete(999999)

    assert result is False


async def test_get_by_ids_with_documents_executes_query_and_returns_models(
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
    integration_document_repo: DocumentRepository,
) -> None:
    user_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(user_data)
    project_data = ProjectCreateDBFactory.build(creator_id=created_user.id)
    created_project = await integration_project_repo.create(project_data)
    documents_data = DocumentCreateDBFactory.batch(2, project_id=created_project.id)
    await integration_document_repo.bulk_create(documents_data)

    results = await integration_project_repo.get_by_ids_with_documents(
        [created_project.id],
    )

    assert len(results) == 1
    retrieved_project = results[0]
    assert retrieved_project.id == created_project.id
    assert len(retrieved_project.documents) == 2  # noqa: PLR2004
    assert retrieved_project.documents[0].project_id == created_project.id


async def test_get_by_ids_with_documents_returns_empty_list_for_empty_input(
    integration_project_repo: ProjectRepository,
) -> None:
    results = await integration_project_repo.get_by_ids_with_documents([])

    assert results == []
