from typing import TYPE_CHECKING

import pytest

from app.core.models.user import User
from app.exceptions.db import ObjectNotFoundError
from app.schemas.user import UserRead
from app.schemas.user import UserUpdateDB
from app.schemas.user import UserUpdateReq
from tests.factories.user import UserCreateReqFactory
from tests.factories.user import UserUpdateReqFactory

if TYPE_CHECKING:
    from unittest.mock import AsyncMock
    from unittest.mock import MagicMock

    from app.services.user import UserService

VALID_HASH = "a" * 60


async def test_create_hashes_password_and_returns_read_schema(
    user_service: UserService,
    mock_user_repo: AsyncMock,
    mock_password_service: MagicMock,
) -> None:
    create_req = UserCreateReqFactory.build(username="validuser")
    mock_password_service.get_password_hash.return_value = VALID_HASH

    expected_model = User(id=1, username=create_req.username, hashed_password=VALID_HASH)
    mock_user_repo.create.return_value = expected_model

    result = await user_service.create(create_req)

    assert isinstance(result, UserRead)
    assert result.username == "validuser"
    mock_password_service.get_password_hash.assert_called_once()


async def test_bulk_create_hashes_passwords_and_returns_read_schemas(
    user_service: UserService,
    mock_user_repo: AsyncMock,
    mock_password_service: MagicMock,
) -> None:
    create_reqs = UserCreateReqFactory.batch(2, username="validuser")
    mock_password_service.get_password_hash.return_value = VALID_HASH

    expected_models = [
        User(id=1, username="validuser", hashed_password=VALID_HASH),
        User(id=2, username="validuser", hashed_password=VALID_HASH),
    ]
    mock_user_repo.bulk_create.return_value = expected_models

    result = await user_service.bulk_create(create_reqs)

    assert len(result) == 2  # noqa: PLR2004
    assert mock_password_service.get_password_hash.call_count == 2  # noqa: PLR2004


async def test_update_modifies_record_with_password_and_returns_read_schema(
    user_service: UserService,
    mock_user_repo: AsyncMock,
    mock_password_service: MagicMock,
) -> None:
    update_req = UserUpdateReqFactory.build(username="newname")
    mock_password_service.get_password_hash.return_value = VALID_HASH

    expected_model = User(id=1, username="newname", hashed_password=VALID_HASH)
    mock_user_repo.update.return_value = expected_model

    result = await user_service.update(1, update_req)

    assert isinstance(result, UserRead)
    assert result.username == "newname"


async def test_update_raises_not_found_error_when_record_does_not_exist(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    update_req = UserUpdateReq(username="newname", password=None)
    mock_user_repo.update.return_value = None

    with pytest.raises(ObjectNotFoundError):
        await user_service.update(999, update_req)


async def test_get_all_executes_query_and_returns_read_schemas(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    expected_models = [
        User(id=1, username="user1", hashed_password=VALID_HASH),
        User(id=2, username="user2", hashed_password=VALID_HASH),
    ]
    mock_user_repo.get_all.return_value = expected_models

    result = await user_service.get_all(skip=0, limit=10)

    assert len(result) == 2  # noqa: PLR2004
    assert isinstance(result[0], UserRead)
    assert result[0].id == 1
    mock_user_repo.get_all.assert_called_once_with(0, 10)


async def test_get_by_id_returns_read_schema_when_record_exists(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    expected_model = User(id=1, username="user1", hashed_password=VALID_HASH)
    mock_user_repo.get_by_id.return_value = expected_model

    result = await user_service.get_by_id(1)

    assert isinstance(result, UserRead)
    assert result.id == 1
    mock_user_repo.get_by_id.assert_called_once_with(1)


async def test_get_by_id_raises_not_found_error_when_record_does_not_exist(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    mock_user_repo.get_by_id.return_value = None

    with pytest.raises(ObjectNotFoundError):
        await user_service.get_by_id(999)


async def test_get_by_username_returns_read_schema_when_record_exists(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    expected_model = User(id=1, username="test_user", hashed_password=VALID_HASH)
    mock_user_repo.get_by_username.return_value = expected_model

    result = await user_service.get_by_username("test_user")

    assert isinstance(result, UserRead)
    assert result.username == "test_user"
    mock_user_repo.get_by_username.assert_called_once_with("test_user")


async def test_get_by_username_raises_not_found_error_when_record_does_not_exist(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    mock_user_repo.get_by_username.return_value = None

    with pytest.raises(ObjectNotFoundError):
        await user_service.get_by_username("non_existent")


async def test_update_modifies_record_without_password_and_returns_read_schema(
    user_service: UserService,
    mock_user_repo: AsyncMock,
    mock_password_service: MagicMock,
) -> None:
    update_req = UserUpdateReq(username="new_username", password=None)
    expected_model = User(id=1, username="new_username", hashed_password="old_pwd")  # noqa: S106
    mock_user_repo.update.return_value = expected_model

    result = await user_service.update(1, update_req)

    assert isinstance(result, UserRead)
    assert result.username == "new_username"
    mock_password_service.get_password_hash.assert_not_called()

    called_arg = mock_user_repo.update.call_args[0][1]
    assert isinstance(called_arg, UserUpdateDB)
    assert called_arg.hashed_password is None


async def test_delete_removes_record_silently_when_successful(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    mock_user_repo.delete.return_value = True

    await user_service.delete(1)

    mock_user_repo.delete.assert_called_once_with(1)


async def test_delete_raises_not_found_error_when_record_does_not_exist(
    user_service: UserService,
    mock_user_repo: AsyncMock,
) -> None:
    mock_user_repo.delete.return_value = False

    with pytest.raises(ObjectNotFoundError):
        await user_service.delete(999)
