from typing import TYPE_CHECKING

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.schemas.user import UserCreateDB

pytestmark = pytest.mark.requires_db


class UserCreateFactory(ModelFactory[UserCreateDB]):
    __model__ = UserCreateDB

    @classmethod
    def hashed_password(cls) -> str:
        return "a" * 60


@pytest.fixture
def user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)


async def test_get_by_username_returns_user_when_exists(
    user_repo: UserRepository,
) -> None:
    target_user_data = UserCreateFactory.build(username="target_user")
    await user_repo.create(target_user_data)

    other_user_data = UserCreateFactory.build(username="other_user")
    await user_repo.create(other_user_data)

    retrieved_user = await user_repo.get_by_username("target_user")

    assert retrieved_user is not None
    assert retrieved_user.username == "target_user"


async def test_get_by_username_returns_none_when_not_found(
    user_repo: UserRepository,
) -> None:
    existing_user_data = UserCreateFactory.build(username="existing_user")
    await user_repo.create(existing_user_data)

    retrieved_user = await user_repo.get_by_username("non_existent_user")

    assert retrieved_user is None
