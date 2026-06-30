from typing import TYPE_CHECKING

import pytest

from app.exceptions.db import ObjectNotFoundError
from app.exceptions.db import UniqueFieldError
from tests.factories.user import UserCreateReqFactory
from tests.factories.user import UserUpdateReqFactory

if TYPE_CHECKING:
    from app.core.auth.password import PasswordService
    from app.repositories.user import UserRepository
    from app.services.user import UserService

pytestmark = pytest.mark.requires_db


async def test_create_inserts_user_and_hashes_password(
    integration_user_service: UserService,
    integration_user_repo: UserRepository,
    password_service: PasswordService,
) -> None:
    req_data = UserCreateReqFactory.build()

    created_user = await integration_user_service.create(req_data)

    assert created_user.id is not None
    assert created_user.username == req_data.username

    db_user = await integration_user_repo.get_by_id(created_user.id)
    assert db_user is not None
    assert db_user.hashed_password != req_data.password.get_secret_value()
    assert password_service.verify_password(req_data.password, db_user.hashed_password)


async def test_bulk_create_inserts_multiple_users_with_hashed_passwords(
    integration_user_service: UserService,
    integration_user_repo: UserRepository,
    password_service: PasswordService,
) -> None:
    req_data_list = UserCreateReqFactory.batch(3)

    results = await integration_user_service.bulk_create(req_data_list)

    assert len(results) == 3  # noqa: PLR2004

    db_user = await integration_user_repo.get_by_id(results[0].id)
    assert db_user is not None
    assert password_service.verify_password(
        req_data_list[0].password, db_user.hashed_password
    )


async def test_update_modifies_user_and_hashes_new_password(
    integration_user_service: UserService,
    integration_user_repo: UserRepository,
    password_service: PasswordService,
) -> None:
    req_data = UserCreateReqFactory.build()
    created_user = await integration_user_service.create(req_data)

    update_req = UserUpdateReqFactory.build(username="new_valid_name123")

    updated_user = await integration_user_service.update(created_user.id, update_req)

    assert updated_user.username == update_req.username

    db_user = await integration_user_repo.get_by_id(updated_user.id)
    assert db_user is not None

    assert update_req.password is not None

    assert password_service.verify_password(update_req.password, db_user.hashed_password)


async def test_update_modifies_user_without_changing_password_if_not_provided(
    integration_user_service: UserService,
    integration_user_repo: UserRepository,
) -> None:
    req_data = UserCreateReqFactory.build()
    created_user = await integration_user_service.create(req_data)
    original_db_user = await integration_user_repo.get_by_id(created_user.id)
    assert original_db_user is not None

    update_req = UserUpdateReqFactory.build(
        username="another_valid_name321", password=None
    )

    updated_user = await integration_user_service.update(created_user.id, update_req)

    assert updated_user.username == update_req.username

    db_user = await integration_user_repo.get_by_id(updated_user.id)
    assert db_user is not None
    assert db_user.hashed_password == original_db_user.hashed_password


async def test_create_raises_unique_field_error_on_duplicate_username(
    integration_user_service: UserService,
) -> None:
    req_data_1 = UserCreateReqFactory.build()
    req_data_2 = UserCreateReqFactory.build(username=req_data_1.username)

    await integration_user_service.create(req_data_1)

    with pytest.raises(UniqueFieldError) as exc_info:
        await integration_user_service.create(req_data_2)

    assert exc_info.value.field_name == "username"


async def test_get_by_username_returns_user_when_exists(
    integration_user_service: UserService,
) -> None:
    req_data = UserCreateReqFactory.build()
    created_user = await integration_user_service.create(req_data)

    result = await integration_user_service.get_by_username(req_data.username)

    assert result.id == created_user.id
    assert result.username == req_data.username


async def test_get_by_username_raises_not_found_error_when_missing(
    integration_user_service: UserService,
) -> None:
    with pytest.raises(ObjectNotFoundError) as exc_info:
        await integration_user_service.get_by_username("non_existent_username")

    assert exc_info.value.table_name == "users"


async def test_update_raises_not_found_error_when_missing(
    integration_user_service: UserService,
) -> None:
    update_req = UserUpdateReqFactory.build()

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await integration_user_service.update(999999, update_req)

    assert exc_info.value.table_name == "users"


async def test_get_by_id_returns_user_when_exists(
    integration_user_service: UserService,
) -> None:
    req_data = UserCreateReqFactory.build()
    created_user = await integration_user_service.create(req_data)

    result = await integration_user_service.get_by_id(created_user.id)

    assert result.id == created_user.id
    assert result.username == req_data.username


async def test_get_by_id_raises_not_found_error_when_missing(
    integration_user_service: UserService,
) -> None:
    with pytest.raises(ObjectNotFoundError):
        await integration_user_service.get_by_id(999999)


async def test_get_all_returns_list_of_users_with_pagination(
    integration_user_service: UserService,
) -> None:
    req_data_list = UserCreateReqFactory.batch(3)
    await integration_user_service.bulk_create(req_data_list)

    results = await integration_user_service.get_all(skip=0, limit=2)

    assert len(results) <= 2  # noqa: PLR2004
    assert type(results) is list


async def test_delete_removes_user(
    integration_user_service: UserService,
) -> None:
    req_data = UserCreateReqFactory.build()
    created_user = await integration_user_service.create(req_data)

    await integration_user_service.delete(created_user.id)

    with pytest.raises(ObjectNotFoundError):
        await integration_user_service.get_by_id(created_user.id)


async def test_delete_raises_not_found_error_when_missing(
    integration_user_service: UserService,
) -> None:
    with pytest.raises(ObjectNotFoundError):
        await integration_user_service.delete(999999)
