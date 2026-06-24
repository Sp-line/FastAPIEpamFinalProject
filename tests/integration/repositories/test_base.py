from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from sqlalchemy.exc import IntegrityError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.db import PostgresErrorCode
from app.exceptions.db import UniqueFieldError
from app.repositories.base import RepositoryBase
from app.repositories.handlers.base import TableErrorHandler
from app.schemas.db import ConstraintRule
from tests.support.dummy_model import DummyCreate
from tests.support.dummy_model import DummyModel
from tests.support.dummy_model import DummyUpdate

pytestmark = pytest.mark.requires_db


class DummyCreateFactory(ModelFactory[DummyCreate]):
    __model__ = DummyCreate


class DummyUpdateFactory(ModelFactory[DummyUpdate]):
    __model__ = DummyUpdate


@pytest.fixture
def dummy_error_handler() -> TableErrorHandler:
    rule = ConstraintRule(
        name="uq_dummy_models_name",
        error_code=PostgresErrorCode.UNIQUE_VIOLATION,
        exception=UniqueFieldError(field_name="name", table_name="dummy_models"),
    )
    return TableErrorHandler(rule)


@pytest.fixture
def dummy_repo(
    db_session: AsyncSession, dummy_error_handler: TableErrorHandler
) -> RepositoryBase[DummyModel, DummyCreate, DummyUpdate]:
    return RepositoryBase(
        model=DummyModel,
        session=db_session,
        table_error_handler=dummy_error_handler,
    )


async def test_get_by_id_returns_model_on_success(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    created_obj = await dummy_repo.create(DummyCreateFactory.build())

    retrieved_obj = await dummy_repo.get_by_id(created_obj.id)

    assert retrieved_obj is not None
    assert retrieved_obj.id == created_obj.id


async def test_get_by_id_returns_none_when_not_found(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    retrieved_obj = await dummy_repo.get_by_id(999999)

    assert retrieved_obj is None


@pytest.mark.parametrize(
    ("input_indices", "expected_count"),
    [
        ([0, 1], 2),
        ([0, 0, 0], 1),
        ([0, 999], 1),
    ],
    ids=["valid_ids", "duplicate_ids", "partially_valid_ids"],
)
async def test_get_by_ids_handles_various_inputs(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
    input_indices: list[int],
    expected_count: int,
) -> None:
    items = await dummy_repo.bulk_create(DummyCreateFactory.batch(2))

    query_ids = [items[i].id if i < len(items) else i for i in input_indices]

    results = await dummy_repo.get_by_ids(query_ids)

    assert len(results) == expected_count


async def test_get_by_ids_returns_empty_list_for_empty_input(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    results = await dummy_repo.get_by_ids([])

    assert results == []


@pytest.mark.parametrize(
    ("skip", "limit", "expected_count"),
    [
        (0, 2, 2),
        (2, 2, 1),
        (0, 0, 0),
        (10, 5, 0),
    ],
    ids=["first_page", "second_page", "zero_limit", "skip_out_of_bounds"],
)
async def test_get_all_applies_pagination(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
    skip: int,
    limit: int,
    expected_count: int,
) -> None:
    await dummy_repo.bulk_create(DummyCreateFactory.batch(3))

    results = await dummy_repo.get_all(skip=skip, limit=limit)

    assert len(results) == expected_count


async def test_create_adds_record_to_db(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    create_data = DummyCreateFactory.build()

    created_obj = await dummy_repo.create(create_data)

    assert created_obj.id is not None
    assert created_obj.name == create_data.name


async def test_create_raises_mapped_exception_on_integrity_error(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    create_data = DummyCreateFactory.build()
    await dummy_repo.create(create_data)

    with pytest.raises(UniqueFieldError, match="name"):
        await dummy_repo.create(create_data)


async def test_bulk_create_adds_multiple_records(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    create_data_list = DummyCreateFactory.batch(3)

    created_objects = await dummy_repo.bulk_create(create_data_list)

    assert len(created_objects) == 3  # noqa: PLR2004
    assert created_objects[0].id is not None


async def test_bulk_create_returns_empty_list_for_empty_input(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    results = await dummy_repo.bulk_create([])

    assert results == []


async def test_bulk_create_raises_mapped_exception_on_integrity_error(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    duplicate_name = "duplicate_name"
    create_data_list = [
        DummyCreate(name=duplicate_name),
        DummyCreate(name=duplicate_name),
    ]

    with pytest.raises(UniqueFieldError, match="name"):
        await dummy_repo.bulk_create(create_data_list)


async def test_update_modifies_existing_record(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    item = await dummy_repo.create(DummyCreateFactory.build())
    update_data = DummyUpdateFactory.build(name="new_unique_name")

    updated_item = await dummy_repo.update(item.id, update_data)

    assert updated_item is not None
    assert updated_item.name == "new_unique_name"


async def test_update_returns_unmodified_record_if_empty_data(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    item = await dummy_repo.create(DummyCreateFactory.build(name="unchanged"))
    empty_update = DummyUpdate()

    updated_item = await dummy_repo.update(item.id, empty_update)

    assert updated_item is not None
    assert updated_item.name == "unchanged"


async def test_update_returns_none_for_non_existent_id(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    update_data = DummyUpdateFactory.build()

    result = await dummy_repo.update(999999, update_data)

    assert result is None


async def test_update_raises_mapped_exception_on_integrity_error(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    await dummy_repo.create(DummyCreateFactory.build(name="target_name"))
    item2 = await dummy_repo.create(DummyCreateFactory.build(name="other_name"))

    update_data = DummyUpdate(name="target_name")

    with pytest.raises(UniqueFieldError, match="name"):
        await dummy_repo.update(item2.id, update_data)


async def test_bulk_update_modifies_multiple_records(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    items = await dummy_repo.bulk_create(DummyCreateFactory.batch(2))
    update_map = {
        items[0].id: DummyUpdate(name="bulk_updated_1"),
        items[1].id: DummyUpdate(name="bulk_updated_2"),
    }

    updated_items = await dummy_repo.bulk_update(update_map)

    assert len(updated_items) == 2  # noqa: PLR2004
    assert {u.name for u in updated_items} == {"bulk_updated_1", "bulk_updated_2"}


async def test_bulk_update_returns_empty_list_for_empty_input(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    results = await dummy_repo.bulk_update({})

    assert results == []


async def test_bulk_update_ignores_empty_update_schemas(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    item = await dummy_repo.create(DummyCreateFactory.build())

    update_map = {item.id: DummyUpdate()}

    results = await dummy_repo.bulk_update(update_map)

    assert results == []


async def test_delete_removes_record_and_returns_true(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    item = await dummy_repo.create(DummyCreateFactory.build())

    is_deleted = await dummy_repo.delete(item.id)

    assert is_deleted is True
    assert await dummy_repo.get_by_id(item.id) is None


async def test_delete_returns_false_for_non_existent_id(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    is_deleted = await dummy_repo.delete(999999)

    assert is_deleted is False


async def test_delete_raises_mapped_exception_on_integrity_error(
    dummy_repo: RepositoryBase[DummyModel, DummyCreate, DummyUpdate],
) -> None:
    item = await dummy_repo.create(DummyCreateFactory.build())

    with (
        patch.object(
            dummy_repo._session,  # noqa: SLF001
            "execute",
            side_effect=IntegrityError("DELETE", {}, Exception("mocked error")),
        ),
        pytest.raises(IntegrityError),
    ):
        await dummy_repo.delete(item.id)
