from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from app.constants.role_type import RoleType
from app.schemas.project import ProjectCreateDB
from app.schemas.project import ProjectRead
from app.schemas.project_member import ProjectMemberCreateDB
from tests.factories.project import ProjectCreateReqFactory

if TYPE_CHECKING:
    from app.usages.projects.create import ProjectCreateUsage


class TestProjectCreateUsage:
    async def test_project_create_usage_creates_project_and_owner_successfully(
        self,
        project_create_usage: ProjectCreateUsage,
        mock_project_repo: AsyncMock,
        mock_project_member_repo: AsyncMock,
        mock_uow: AsyncMock,
    ) -> None:
        creator_id = 42
        req_data = ProjectCreateReqFactory.build()

        mock_db_project = MagicMock()
        mock_db_project.id = 1
        mock_db_project.name = req_data.name
        mock_db_project.description = req_data.description
        mock_db_project.creator_id = creator_id

        mock_project_repo.create.return_value = mock_db_project

        result = await project_create_usage(data=req_data, creator_id=creator_id)

        mock_uow.__aenter__.assert_awaited_once()

        expected_project_create_db = ProjectCreateDB(
            **req_data.model_dump(), creator_id=creator_id
        )
        mock_project_repo.create.assert_awaited_once()
        actual_project_call_args = mock_project_repo.create.call_args.args[0]
        assert (
            actual_project_call_args.model_dump()
            == expected_project_create_db.model_dump()
        )

        expected_member_create_db = ProjectMemberCreateDB(
            role=RoleType.OWNER,
            user_id=creator_id,
            project_id=mock_db_project.id,
        )
        mock_project_member_repo.create.assert_awaited_once()
        actual_member_call_args = mock_project_member_repo.create.call_args.args[0]
        assert (
            actual_member_call_args.model_dump()
            == expected_member_create_db.model_dump()
        )

        assert isinstance(result, ProjectRead)
        assert result.id == mock_db_project.id
        assert result.name == req_data.name

    async def test_project_create_usage_halts_if_project_creation_fails(
        self,
        project_create_usage: ProjectCreateUsage,
        mock_project_repo: AsyncMock,
        mock_project_member_repo: AsyncMock,
        mock_uow: AsyncMock,
    ) -> None:
        creator_id = 42
        req_data = ProjectCreateReqFactory.build()

        expected_exception = Exception("Database error during project creation")
        mock_project_repo.create.side_effect = expected_exception

        with pytest.raises(Exception, match="Database error during project creation"):
            await project_create_usage(data=req_data, creator_id=creator_id)

        mock_project_repo.create.assert_awaited_once()
        mock_project_member_repo.create.assert_not_called()
        mock_uow.__aexit__.assert_awaited_once()

    async def test_project_create_usage_bubbles_up_error_if_member_creation_fails(
        self,
        project_create_usage: ProjectCreateUsage,
        mock_project_repo: AsyncMock,
        mock_project_member_repo: AsyncMock,
        mock_uow: AsyncMock,
    ) -> None:
        creator_id = 42
        req_data = ProjectCreateReqFactory.build()

        mock_db_project = MagicMock()
        mock_db_project.id = 1
        mock_project_repo.create.return_value = mock_db_project

        expected_exception = Exception("Database error during member creation")
        mock_project_member_repo.create.side_effect = expected_exception

        with pytest.raises(Exception, match="Database error during member creation"):
            await project_create_usage(data=req_data, creator_id=creator_id)

        mock_project_repo.create.assert_awaited_once()
        mock_project_member_repo.create.assert_awaited_once()
        mock_uow.__aexit__.assert_awaited_once()
