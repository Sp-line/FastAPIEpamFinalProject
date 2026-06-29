from contextlib import suppress
from typing import TYPE_CHECKING

import pytest

from app.constants.role_type import RoleType
from app.exceptions.db import RelatedObjectNotFoundError
from app.exceptions.db import UniqueError
from app.exceptions.db import UniqueFieldError
from app.schemas.project_member import ProjectMemberUpdateDB
from tests.factories.project import ProjectCreateDBFactory
from tests.factories.project_member import ProjectMemberCreateDBFactory
from tests.factories.user import UserCreateDBFactory

if TYPE_CHECKING:
    from app.repositories.project import ProjectRepository
    from app.repositories.project_member import ProjectMemberAssociationRepository
    from app.repositories.user import UserRepository

pytestmark = pytest.mark.requires_db


async def test_create_inserts_record_in_db_and_returns_model(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    member_data = ProjectMemberCreateDBFactory.build(
        user_id=user.id, project_id=project.id, role=RoleType.PARTICIPANT
    )

    created_member = await integration_project_member_repo.create(member_data)

    assert created_member.id is not None
    assert created_member.user_id == user.id
    assert created_member.project_id == project.id
    assert created_member.role == member_data.role


async def test_create_raises_related_object_not_found_error_on_invalid_user_id(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    member_data = ProjectMemberCreateDBFactory.build(
        user_id=999999, project_id=project.id
    )

    with pytest.raises(RelatedObjectNotFoundError) as exc_info:
        await integration_project_member_repo.create(member_data)

    assert exc_info.value.field_name == "user_id"


async def test_create_raises_related_object_not_found_error_on_invalid_project_id(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    member_data = ProjectMemberCreateDBFactory.build(user_id=user.id, project_id=999999)

    with pytest.raises(RelatedObjectNotFoundError) as exc_info:
        await integration_project_member_repo.create(member_data)

    assert exc_info.value.field_name == "project_id"


async def test_create_raises_unique_error_on_duplicate_user_project_pair(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )

    user_2 = await integration_user_repo.create(UserCreateDBFactory.build())

    member_data_1 = ProjectMemberCreateDBFactory.build(
        user_id=user_2.id, project_id=project.id, role=RoleType.PARTICIPANT
    )
    member_data_2 = ProjectMemberCreateDBFactory.build(
        user_id=user_2.id, project_id=project.id, role=RoleType.PARTICIPANT
    )

    await integration_project_member_repo.create(member_data_1)

    with pytest.raises(UniqueError):
        await integration_project_member_repo.create(member_data_2)


async def test_create_raises_unique_field_error_on_multiple_owners(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_1 = await integration_user_repo.create(UserCreateDBFactory.build())
    user_2 = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user_1.id)
    )

    member_data_1 = ProjectMemberCreateDBFactory.build(
        user_id=user_1.id, project_id=project.id, role=RoleType.OWNER
    )
    member_data_2 = ProjectMemberCreateDBFactory.build(
        user_id=user_2.id, project_id=project.id, role=RoleType.OWNER
    )

    with suppress(Exception):
        await integration_project_member_repo.create(member_data_1)

    with pytest.raises(UniqueFieldError) as exc_info:
        await integration_project_member_repo.create(member_data_2)

    assert exc_info.value.field_name == "role"


async def test_get_by_user_and_project_returns_model_when_exists(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    user_2 = await integration_user_repo.create(UserCreateDBFactory.build())

    member = await integration_project_member_repo.create(
        ProjectMemberCreateDBFactory.build(
            user_id=user_2.id, project_id=project.id, role=RoleType.PARTICIPANT
        )
    )

    result = await integration_project_member_repo.get_by_user_and_project(
        user_2.id, project.id
    )

    assert result is not None
    assert result.id == member.id
    assert result.user_id == user_2.id
    assert result.project_id == project.id


async def test_get_by_user_and_project_returns_none_when_not_exists(
    integration_project_member_repo: ProjectMemberAssociationRepository,
) -> None:
    result = await integration_project_member_repo.get_by_user_and_project(999, 999)

    assert result is None


async def test_get_project_ids_by_user_and_roles_returns_filtered_ids(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    proj_1 = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    proj_2 = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    proj_3 = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )

    user_target = await integration_user_repo.create(UserCreateDBFactory.build())

    await integration_project_member_repo.bulk_create(
        [
            ProjectMemberCreateDBFactory.build(
                user_id=user_target.id, project_id=proj_1.id, role=RoleType.OWNER
            ),
            ProjectMemberCreateDBFactory.build(
                user_id=user_target.id, project_id=proj_2.id, role=RoleType.PARTICIPANT
            ),
            ProjectMemberCreateDBFactory.build(
                user_id=user_target.id, project_id=proj_3.id, role=RoleType.OWNER
            ),
        ]
    )

    roles = {RoleType.OWNER}
    project_ids = (
        await integration_project_member_repo.get_project_ids_by_user_and_roles(
            user_target.id, roles
        )
    )

    assert len(project_ids) == 2  # noqa: PLR2004
    assert proj_1.id in project_ids
    assert proj_3.id in project_ids
    assert proj_2.id not in project_ids


async def test_get_project_ids_by_user_and_roles_returns_empty_if_no_roles_passed(
    integration_project_member_repo: ProjectMemberAssociationRepository,
) -> None:
    result = await integration_project_member_repo.get_project_ids_by_user_and_roles(
        1, set()
    )

    assert result == []


async def test_bulk_create_inserts_multiple_records(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_1 = await integration_user_repo.create(UserCreateDBFactory.build())
    user_2 = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user_1.id)
    )

    members_data = [
        ProjectMemberCreateDBFactory.build(
            user_id=user_1.id, project_id=project.id, role=RoleType.PARTICIPANT
        ),
        ProjectMemberCreateDBFactory.build(
            user_id=user_2.id, project_id=project.id, role=RoleType.PARTICIPANT
        ),
    ]

    created_members = await integration_project_member_repo.bulk_create(members_data)

    assert len(created_members) == 2  # noqa: PLR2004
    assert created_members[0].id is not None
    assert created_members[1].id is not None


async def test_update_modifies_existing_record(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    user_target = await integration_user_repo.create(UserCreateDBFactory.build())

    member = await integration_project_member_repo.create(
        ProjectMemberCreateDBFactory.build(
            user_id=user_target.id, project_id=project.id, role=RoleType.OWNER
        )
    )

    update_data = ProjectMemberUpdateDB(role=RoleType.PARTICIPANT)

    updated_member = await integration_project_member_repo.update(member.id, update_data)

    assert updated_member is not None
    assert updated_member.role == RoleType.PARTICIPANT
    assert updated_member.id == member.id


async def test_delete_removes_record_from_db(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user.id)
    )
    user_target = await integration_user_repo.create(UserCreateDBFactory.build())

    member = await integration_project_member_repo.create(
        ProjectMemberCreateDBFactory.build(
            user_id=user_target.id, project_id=project.id, role=RoleType.PARTICIPANT
        )
    )

    is_deleted = await integration_project_member_repo.delete(member.id)
    retrieved_member = await integration_project_member_repo.get_by_id(member.id)

    assert is_deleted is True
    assert retrieved_member is None


async def test_get_by_ids_returns_correct_models(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_1 = await integration_user_repo.create(UserCreateDBFactory.build())
    user_2 = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user_1.id)
    )

    members = await integration_project_member_repo.bulk_create(
        [
            ProjectMemberCreateDBFactory.build(
                user_id=user_1.id, project_id=project.id, role=RoleType.PARTICIPANT
            ),
            ProjectMemberCreateDBFactory.build(
                user_id=user_2.id, project_id=project.id, role=RoleType.PARTICIPANT
            ),
        ]
    )

    target_ids = [members[0].id]

    results = await integration_project_member_repo.get_by_ids(target_ids)

    assert len(results) == 1
    assert results[0].id == members[0].id


async def test_get_all_returns_all_models_with_pagination(
    integration_project_member_repo: ProjectMemberAssociationRepository,
    integration_project_repo: ProjectRepository,
    integration_user_repo: UserRepository,
) -> None:
    user_1 = await integration_user_repo.create(UserCreateDBFactory.build())
    user_2 = await integration_user_repo.create(UserCreateDBFactory.build())
    user_3 = await integration_user_repo.create(UserCreateDBFactory.build())
    project = await integration_project_repo.create(
        ProjectCreateDBFactory.build(creator_id=user_1.id)
    )

    await integration_project_member_repo.bulk_create(
        [
            ProjectMemberCreateDBFactory.build(
                user_id=user_1.id, project_id=project.id, role=RoleType.PARTICIPANT
            ),
            ProjectMemberCreateDBFactory.build(
                user_id=user_2.id, project_id=project.id, role=RoleType.PARTICIPANT
            ),
            ProjectMemberCreateDBFactory.build(
                user_id=user_3.id, project_id=project.id, role=RoleType.PARTICIPANT
            ),
        ]
    )

    results = await integration_project_member_repo.get_all(skip=0, limit=2)

    assert len(results) <= 2  # noqa: PLR2004
