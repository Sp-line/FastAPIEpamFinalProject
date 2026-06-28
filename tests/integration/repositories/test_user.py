from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from app.core.models.user import User
from app.exceptions.db import CheckConstraintError
from app.exceptions.db import UniqueFieldError
from app.schemas.user import UserCreateDB
from app.schemas.user import UserUpdateDB
from tests.factories.user import UserCreateDBFactory
from tests.factories.user import UserUpdateDBFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.repositories.user import UserRepository

pytestmark = pytest.mark.requires_db


async def test_update_modifies_existing_record_and_returns_model(
    integration_user_repo: UserRepository,
    db_session: AsyncSession,
) -> None:
    create_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(create_data)

    update_data = UserUpdateDB(username="new_unique_username")

    result = await integration_user_repo.update(created_user.id, update_data)

    assert result is not None
    assert result.id == created_user.id
    assert result.username == update_data.username

    await db_session.refresh(created_user)
    assert created_user.username == update_data.username


async def test_update_raises_unique_field_error_on_duplicate_username(
    integration_user_repo: UserRepository,
) -> None:
    user1_data = UserCreateDBFactory.build()
    user2_data = UserCreateDBFactory.build()
    await integration_user_repo.create(user1_data)
    created_user2 = await integration_user_repo.create(user2_data)

    update_data = UserUpdateDB(username=user1_data.username)

    with pytest.raises(UniqueFieldError):
        await integration_user_repo.update(created_user2.id, update_data)


async def test_bulk_update_modifies_multiple_records_and_returns_models(
    integration_user_repo: UserRepository,
) -> None:
    users_data = UserCreateDBFactory.batch(2)
    created_users = await integration_user_repo.bulk_create(users_data)
    user1, user2 = created_users[0], created_users[1]

    update_map = {
        user1.id: UserUpdateDB(username="bulk_updated_user_1"),
        user2.id: UserUpdateDB(username="bulk_updated_user_2"),
    }

    result = await integration_user_repo.bulk_update(update_map)

    assert len(result) == 2  # noqa: PLR2004
    updated_users = {user.id: user for user in result}
    assert updated_users[user1.id].username == update_map[user1.id].username
    assert updated_users[user2.id].username == update_map[user2.id].username


async def test_bulk_update_raises_unique_field_error_on_duplicate_username(
    integration_user_repo: UserRepository,
) -> None:
    users_data = UserCreateDBFactory.batch(2)
    created_users = await integration_user_repo.bulk_create(users_data)
    user1, user2 = created_users[0], created_users[1]

    update_map = {
        user2.id: UserUpdateDB(username=user1.username),
    }

    with pytest.raises(UniqueFieldError):
        await integration_user_repo.bulk_update(update_map)


async def test_create_inserts_record_in_db_and_returns_model(
    integration_user_repo: UserRepository,
    db_session: AsyncSession,
) -> None:
    create_data = UserCreateDBFactory.build()

    result = await integration_user_repo.create(create_data)

    assert result.id is not None
    assert result.username == create_data.username
    assert result.hashed_password == create_data.hashed_password

    stmt = select(User).where(User.id == result.id)
    db_result = await db_session.scalar(stmt)
    assert db_result is not None
    assert db_result.username == create_data.username


async def test_create_raises_unique_field_error_on_duplicate_username(
    integration_user_repo: UserRepository,
) -> None:
    create_data = UserCreateDBFactory.build()
    await integration_user_repo.create(create_data)

    duplicate_data = UserCreateDBFactory.build(username=create_data.username)

    with pytest.raises(UniqueFieldError):
        await integration_user_repo.create(duplicate_data)


@pytest.mark.parametrize(
    ("username", "hashed_password"),
    [
        ("a", "valid_hash_length_string_1234567890"),
        ("valid_username", "short"),
    ],
    ids=["short_username", "short_password"],
)
async def test_create_raises_check_constraint_error_on_invalid_lengths(
    integration_user_repo: UserRepository,
    username: str,
    hashed_password: str,
) -> None:
    create_data = UserCreateDB.model_construct(
        username=username,
        hashed_password=hashed_password,
    )

    with pytest.raises(CheckConstraintError):
        await integration_user_repo.create(create_data)


async def test_get_by_username_returns_model_when_record_exists(
    integration_user_repo: UserRepository,
) -> None:
    create_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(create_data)

    result = await integration_user_repo.get_by_username(create_data.username)

    assert result is not None
    assert result.id == created_user.id
    assert result.username == create_data.username


async def test_get_by_username_returns_none_when_record_does_not_exist(
    integration_user_repo: UserRepository,
) -> None:
    result = await integration_user_repo.get_by_username("non_existent_username")

    assert result is None


async def test_get_by_id_returns_model_when_record_exists(
    integration_user_repo: UserRepository,
) -> None:
    create_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(create_data)

    result = await integration_user_repo.get_by_id(created_user.id)

    assert result is not None
    assert result.id == created_user.id


async def test_get_by_id_returns_none_when_record_does_not_exist(
    integration_user_repo: UserRepository,
) -> None:
    result = await integration_user_repo.get_by_id(999999)

    assert result is None


async def test_get_by_ids_returns_models_for_existing_records(
    integration_user_repo: UserRepository,
) -> None:
    users_data = UserCreateDBFactory.batch(3)
    created_users = [await integration_user_repo.create(data) for data in users_data]
    target_ids = [created_users[0].id, created_users[2].id]

    result = await integration_user_repo.get_by_ids(target_ids)

    assert len(result) == 2  # noqa: PLR2004
    retrieved_ids = {user.id for user in result}
    assert target_ids[0] in retrieved_ids
    assert target_ids[1] in retrieved_ids


async def test_get_by_ids_returns_empty_list_for_empty_input(
    integration_user_repo: UserRepository,
) -> None:
    result = await integration_user_repo.get_by_ids([])

    assert result == []


async def test_get_all_returns_paginated_models(
    integration_user_repo: UserRepository,
) -> None:
    users_data = UserCreateDBFactory.batch(5)
    await integration_user_repo.bulk_create(users_data)

    result = await integration_user_repo.get_all(skip=1, limit=2)

    assert len(result) == 2  # noqa: PLR2004
    assert isinstance(result[0], User)


async def test_bulk_create_inserts_multiple_records_and_returns_models(
    integration_user_repo: UserRepository,
    db_session: AsyncSession,
) -> None:
    create_data_list = UserCreateDBFactory.batch(3)

    result = await integration_user_repo.bulk_create(create_data_list)

    assert len(result) == 3  # noqa: PLR2004
    stmt = select(User).where(User.id.in_([user.id for user in result]))
    db_result = await db_session.scalars(stmt)
    assert len(db_result.all()) == 3  # noqa: PLR2004


async def test_bulk_create_raises_unique_field_error_on_duplicate_data(
    integration_user_repo: UserRepository,
) -> None:
    duplicate_username = "duplicate_username"
    create_data_list = [
        UserCreateDBFactory.build(username=duplicate_username),
        UserCreateDBFactory.build(username=duplicate_username),
    ]

    with pytest.raises(UniqueFieldError):
        await integration_user_repo.bulk_create(create_data_list)


async def test_update_returns_none_when_record_does_not_exist(
    integration_user_repo: UserRepository,
) -> None:
    update_data = UserUpdateDBFactory.build()

    result = await integration_user_repo.update(999999, update_data)

    assert result is None


async def test_delete_removes_record_and_returns_true(
    integration_user_repo: UserRepository,
    db_session: AsyncSession,
) -> None:
    create_data = UserCreateDBFactory.build()
    created_user = await integration_user_repo.create(create_data)

    result = await integration_user_repo.delete(created_user.id)

    assert result is True
    stmt = select(User).where(User.id == created_user.id)
    db_result = await db_session.scalar(stmt)
    assert db_result is None


async def test_delete_returns_false_when_record_does_not_exist(
    integration_user_repo: UserRepository,
) -> None:
    result = await integration_user_repo.delete(999999)

    assert result is False
