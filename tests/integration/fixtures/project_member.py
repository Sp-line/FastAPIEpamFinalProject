from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from repositories.project_member import ProjectMemberAssociationRepository


@pytest.fixture
def integration_project_member_repo(
    db_session: AsyncSession,
) -> ProjectMemberAssociationRepository:
    return ProjectMemberAssociationRepository(session=db_session)
