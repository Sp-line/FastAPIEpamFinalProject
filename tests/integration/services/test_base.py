from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel
from pydantic import ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.db import ObjectNotFoundError
from app.repositories.base import RepositoryBase
from app.repositories.unit_of_work import UnitOfWork
from app.services.base import ServiceBase
from tests.support.dummy_model import DummyModel


class DummyDBModel(BaseModel):
    id: int
    name: str


class DummyRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DummyCreate(BaseModel):
    name: str


class DummyUpdate(BaseModel):
    name: str | None = None


class DummyDBCreate(BaseModel):
    name: str


class DummyDBUpdate(BaseModel):
    name: str | None = None


type DummyRepoType = RepositoryBase[
    DummyModel,
    DummyDBCreate,
    DummyDBUpdate,
    AsyncSession,
]
type DummyServiceType = ServiceBase[
    DummyRepoType,
    DummyRead,
    DummyCreate,
    DummyUpdate,
    DummyDBCreate,
    DummyDBUpdate,
]


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock(spec=RepositoryBase)
    repo.get_all = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    repo.bulk_create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_uow() -> MagicMock:
    uow = MagicMock(spec=UnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def base_service(mock_repo: MagicMock, mock_uow: MagicMock) -> DummyServiceType:
    return ServiceBase(
        repository=mock_repo,
        unit_of_work=mock_uow,
        table_name="dummy_table",
        read_schema=DummyRead,
        db_create_schema=DummyDBCreate,
        db_update_schema=DummyDBUpdate,
    )


@pytest.mark.parametrize(
    ("skip", "limit", "db_records"),
    [
        (0, 10, [DummyDBModel(id=1, name="Item 1"), DummyDBModel(id=2, name="Item 2")]),
        (5, 5, []),
    ],
    ids=["returns_mapped_list", "returns_empty_list"],
)
async def test_get_all_returns_mapped_schemas(
    base_service: DummyServiceType,
    mock_repo: MagicMock,
    skip: int,
    limit: int,
    db_records: list[DummyDBModel],
) -> None:
    mock_repo.get_all.return_value = db_records

    results = await base_service.get_all(skip=skip, limit=limit)

    mock_repo.get_all.assert_awaited_once_with(skip, limit)
    assert len(results) == len(db_records)
    if results:
        assert isinstance(results[0], DummyRead)
        assert results[0].id == db_records[0].id


async def test_get_by_id_returns_mapped_schema(
    base_service: DummyServiceType, mock_repo: MagicMock
) -> None:
    db_model = DummyDBModel(id=1, name="Test Item")
    mock_repo.get_by_id.return_value = db_model

    result = await base_service.get_by_id(1)

    mock_repo.get_by_id.assert_awaited_once_with(1)
    assert isinstance(result, DummyRead)
    assert result.id == 1
    assert result.name == "Test Item"


async def test_get_by_id_raises_not_found(
    base_service: DummyServiceType, mock_repo: MagicMock
) -> None:
    mock_repo.get_by_id.return_value = None

    with pytest.raises(ObjectNotFoundError, match="dummy_table"):
        await base_service.get_by_id(999)


async def test_create_uses_uow_and_returns_mapped_schema(
    base_service: DummyServiceType, mock_repo: MagicMock, mock_uow: MagicMock
) -> None:
    create_dto = DummyCreate(name="New Item")
    db_model = DummyDBModel(id=1, name="New Item")
    mock_repo.create.return_value = db_model

    result = await base_service.create(create_dto)

    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

    mock_repo.create.assert_awaited_once()
    repo_arg = mock_repo.create.call_args[0][0]
    assert isinstance(repo_arg, DummyDBCreate)

    assert isinstance(result, DummyRead)
    assert result.id == 1


async def test_bulk_create_uses_uow_and_returns_mapped_schemas(
    base_service: DummyServiceType, mock_repo: MagicMock, mock_uow: MagicMock
) -> None:
    dtos = [DummyCreate(name="Item A"), DummyCreate(name="Item B")]
    db_models = [DummyDBModel(id=1, name="Item A"), DummyDBModel(id=2, name="Item B")]
    mock_repo.bulk_create.return_value = db_models

    results = await base_service.bulk_create(dtos)

    mock_uow.__aenter__.assert_awaited_once()
    mock_repo.bulk_create.assert_awaited_once()
    assert len(results) == 2  # noqa: PLR2004
    assert isinstance(results[0], DummyRead)


async def test_update_excludes_unset_fields_and_returns_mapped_schema(
    base_service: DummyServiceType, mock_repo: MagicMock, mock_uow: MagicMock
) -> None:
    update_dto = DummyUpdate(name="Updated Item")
    db_model = DummyDBModel(id=1, name="Updated Item")
    mock_repo.update.return_value = db_model

    result = await base_service.update(1, update_dto)

    mock_uow.__aenter__.assert_awaited_once()
    mock_repo.update.assert_awaited_once()

    repo_args = mock_repo.update.call_args[0]
    assert repo_args[0] == 1
    assert isinstance(repo_args[1], DummyDBUpdate)

    assert isinstance(result, DummyRead)
    assert result.name == "Updated Item"


async def test_update_raises_not_found(
    base_service: DummyServiceType, mock_repo: MagicMock
) -> None:
    update_dto = DummyUpdate(name="Lost Item")
    mock_repo.update.return_value = None

    with pytest.raises(ObjectNotFoundError, match="dummy_table"):
        await base_service.update(999, update_dto)


async def test_delete_uses_uow_and_returns_none(
    base_service: DummyServiceType, mock_repo: MagicMock, mock_uow: MagicMock
) -> None:
    mock_repo.delete.return_value = True

    await base_service.delete(1)

    mock_uow.__aenter__.assert_awaited_once()
    mock_repo.delete.assert_awaited_once_with(1)


async def test_delete_raises_not_found(
    base_service: DummyServiceType, mock_repo: MagicMock
) -> None:
    mock_repo.delete.return_value = False

    with pytest.raises(ObjectNotFoundError, match="dummy_table"):
        await base_service.delete(999)
