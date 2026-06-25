from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from app.core.auth.password import PasswordService
from app.exceptions.db import ObjectNotFoundError
from app.repositories.user import UserRepository
from app.schemas.user import UserCreateDB
from app.schemas.user import UserCreateReq
from app.schemas.user import UserRead
from app.schemas.user import UserUpdateDB
from app.schemas.user import UserUpdateReq
from app.services.user import UserService

VALID_FAKE_HASH = "a" * 60


@pytest.fixture
def mock_user_repo() -> MagicMock:
    repo = MagicMock(spec=UserRepository)
    repo.get_by_username = AsyncMock()
    return repo


@pytest.fixture
def mock_password_service() -> MagicMock:
    service = MagicMock(spec=PasswordService)
    service.get_password_hash.return_value = VALID_FAKE_HASH
    return service


@pytest.fixture
def user_service(
    mock_user_repo: MagicMock,
    mock_uow: MagicMock,
    mock_password_service: MagicMock,
) -> UserService:
    return UserService(
        repository=mock_user_repo,
        unit_of_work=mock_uow,
        password_service=mock_password_service,
    )


class DummyUserDBModel:
    def __init__(self, obj_id: int, username: str, hashed_password: str) -> None:
        self.id = obj_id
        self.username = username
        self.hashed_password = hashed_password


async def test_get_by_username_returns_mapped_schema_on_success(
    user_service: UserService, mock_user_repo: MagicMock
) -> None:
    db_user = DummyUserDBModel(
        obj_id=1, username="test_user", hashed_password=VALID_FAKE_HASH
    )
    mock_user_repo.get_by_username.return_value = db_user

    result = await user_service.get_by_username("test_user")

    mock_user_repo.get_by_username.assert_awaited_once_with("test_user")
    assert isinstance(result, UserRead)
    assert result.id == 1
    assert result.username == "test_user"


async def test_get_by_username_raises_not_found_on_missing_user(
    user_service: UserService, mock_user_repo: MagicMock
) -> None:
    mock_user_repo.get_by_username.return_value = None

    with pytest.raises(ObjectNotFoundError) as exc_info:
        await user_service.get_by_username("missing_user")

    assert exc_info.value.table_name == "users"
    assert exc_info.value.conditions == {"username": "missing_user"}


def test_create_data_transfer_hashes_password_and_maps_fields(
    user_service: UserService, mock_password_service: MagicMock
) -> None:
    create_req = UserCreateReq(username="new_user", password=SecretStr("ValidPass123!"))

    result = user_service._create_data_transfer(create_req)  # noqa: SLF001

    mock_password_service.get_password_hash.assert_called_once_with(
        SecretStr("ValidPass123!")
    )
    assert isinstance(result, UserCreateDB)
    assert result.username == "new_user"
    assert result.hashed_password == VALID_FAKE_HASH


def test_bulk_create_data_transfer_maps_multiple_items(
    user_service: UserService, mock_password_service: MagicMock
) -> None:
    requests = [
        UserCreateReq(username="user_1", password=SecretStr("ValidPass123!")),
        UserCreateReq(username="user_2", password=SecretStr("ValidPass456!")),
    ]

    results = user_service._bulk_create_data_transfer(requests)  # noqa: SLF001

    assert mock_password_service.get_password_hash.call_count == 2  # noqa: PLR2004
    assert len(results) == 2  # noqa: PLR2004
    assert all(isinstance(res, UserCreateDB) for res in results)
    assert results[0].username == "user_1"
    assert results[1].username == "user_2"


def test_bulk_create_data_transfer_returns_empty_list_for_empty_input(
    user_service: UserService, mock_password_service: MagicMock
) -> None:
    results = user_service._bulk_create_data_transfer([])  # noqa: SLF001

    mock_password_service.get_password_hash.assert_not_called()
    assert results == []


@pytest.mark.parametrize(
    ("update_req", "expected_hash_called", "expected_db_fields"),
    [
        (
            UserUpdateReq(username="updated_name"),
            False,
            {"username": "updated_name"},
        ),
        (
            UserUpdateReq(password=SecretStr("NewValidPass123!")),
            True,
            {"hashed_password": VALID_FAKE_HASH},
        ),
        (
            UserUpdateReq(
                username="updated_name", password=SecretStr("NewValidPass123!")
            ),
            True,
            {"username": "updated_name", "hashed_password": VALID_FAKE_HASH},
        ),
    ],
    ids=["only_username", "only_password", "both_username_and_password"],
)
def test_update_data_transfer_handles_password_hashing_correctly(
    user_service: UserService,
    mock_password_service: MagicMock,
    update_req: UserUpdateReq,
    expected_hash_called: bool,  # noqa: FBT001
    expected_db_fields: dict[str, str],
) -> None:
    result = user_service._update_data_transfer(update_req)  # noqa: SLF001

    if expected_hash_called:
        mock_password_service.get_password_hash.assert_called_once()
    else:
        mock_password_service.get_password_hash.assert_not_called()

    assert isinstance(result, UserUpdateDB)

    result_dict = result.model_dump(exclude_unset=True)
    assert result_dict == expected_db_fields
