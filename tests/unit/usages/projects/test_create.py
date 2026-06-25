from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import MagicMock

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from app.constants import RoleType
from app.constants.project import ProjectLimits
from app.exceptions.db import UniqueFieldError
from app.schemas.project import ProjectCreateDB
from app.schemas.project import ProjectCreateReq
from app.schemas.project import ProjectRead
from app.schemas.project_member import ProjectMemberCreateDB
from app.usages.projects.create import ProjectCreateUsage

TEST_PROJECT_ID = 100


class ProjectCreateReqFactory(ModelFactory[ProjectCreateReq]):
    __model__ = ProjectCreateReq


class ProjectCreateDBFactory(ModelFactory[ProjectCreateDB]):
    __model__ = ProjectCreateDB


class ProjectReadFactory(ModelFactory[ProjectRead]):
    __model__ = ProjectRead


class ProjectMemberCreateDBFactory(ModelFactory[ProjectMemberCreateDB]):
    __model__ = ProjectMemberCreateDB


@pytest.fixture
def project_create_usage(
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    mock_uow: MagicMock,
) -> ProjectCreateUsage:
    return ProjectCreateUsage(
        repository=mock_project_repo,
        project_member_repository=mock_project_member_repo,
        unit_of_work=mock_uow,
    )


@pytest.mark.parametrize(
    ("project_name", "description", "creator_id"),
    [
        ("A" * ProjectLimits.NAME_MIN, None, 1),
        ("B" * ProjectLimits.NAME_MAX, "Project description", 42),
    ],
    ids=["min_name_without_description", "max_name_with_description"],
)
async def test_call_creates_project_and_owner_membership(  # noqa: PLR0913
    project_create_usage: ProjectCreateUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    mock_uow: MagicMock,
    project_name: str,
    description: str | None,
    creator_id: int,
) -> None:
    data = ProjectCreateReqFactory.build(name=project_name, description=description)
    created_project = ProjectReadFactory.build(
        id=TEST_PROJECT_ID,
        name=project_name,
        description=description,
        creator_id=creator_id,
    )
    mock_project_repo.create.return_value = created_project

    result = await project_create_usage(data, creator_id)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_project_repo.create.assert_awaited_once_with(
        ProjectCreateDBFactory.build(
            name=project_name,
            description=description,
            creator_id=creator_id,
        )
    )
    mock_project_member_repo.create.assert_awaited_once_with(
        ProjectMemberCreateDBFactory.build(
            role=RoleType.OWNER,
            user_id=creator_id,
            project_id=TEST_PROJECT_ID,
        )
    )

    assert isinstance(result, ProjectRead)
    assert result.id == TEST_PROJECT_ID
    assert result.name == project_name
    assert result.description == description
    assert result.creator_id == creator_id


async def test_call_propagates_project_repository_error_and_skips_membership_creation(
    project_create_usage: ProjectCreateUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    mock_uow: MagicMock,
) -> None:
    data = ProjectCreateReqFactory.build(name="Valid project", description=None)
    mock_project_repo.create.side_effect = UniqueFieldError(
        field_name="name",
        table_name="projects",
    )

    with pytest.raises(UniqueFieldError, match="name"):
        await project_create_usage(data, 7)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()
    mock_project_repo.create.assert_awaited_once()
    mock_project_member_repo.create.assert_not_awaited()


async def test_call_propagates_membership_repository_error_after_project_creation(
    project_create_usage: ProjectCreateUsage,
    mock_project_repo: MagicMock,
    mock_project_member_repo: MagicMock,
    mock_uow: MagicMock,
) -> None:
    data = ProjectCreateReqFactory.build(name="Another project", description="desc")
    mock_project_repo.create.return_value = ProjectReadFactory.build(
        id=101,
        name=data.name,
        description=data.description,
        creator_id=7,
    )
    mock_project_member_repo.create.side_effect = RuntimeError("membership failed")

    with pytest.raises(RuntimeError, match="membership failed"):
        await project_create_usage(data, 7)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()
    mock_project_repo.create.assert_awaited_once()
    mock_project_member_repo.create.assert_awaited_once()
