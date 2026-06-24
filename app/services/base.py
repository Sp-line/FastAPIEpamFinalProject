from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

from pydantic import BaseModel

from app.exceptions.db import ObjectNotFoundError
from app.repositories.base import CommandRepositoryBase
from app.repositories.base import QueryRepositoryBase
from app.repositories.base import RepositoryBase
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001


class QueryServiceBase[
    TQueryRepository: QueryRepositoryBase[Any, Any],
    TReadSchema: BaseModel,
]:
    def __init__(
        self,
        repository: TQueryRepository,
        table_name: str,
        read_schema: type[TReadSchema],
    ) -> None:
        self._repository = repository
        self._table_name = table_name
        self._read_schema = read_schema

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[TReadSchema]:
        return [
            self._read_schema.model_validate(obj)
            for obj in await self._repository.get_all(skip, limit)
        ]

    async def get_by_id(self, obj_id: int) -> TReadSchema:
        if not (obj := await self._repository.get_by_id(obj_id)):
            raise ObjectNotFoundError(obj_id=obj_id, table_name=self._table_name)
        return self._read_schema.model_validate(obj)


class CommandServiceBase[
    TCommandRepository: CommandRepositoryBase[Any, Any, Any, Any],
    TReadSchema: BaseModel,
    TCreateSchema: BaseModel,
    TUpdateSchema: BaseModel,
    TDBCreateSchema: BaseModel,
    TDBUpdateSchema: BaseModel,
]:
    def __init__(  # noqa: PLR0913
        self,
        repository: TCommandRepository,
        unit_of_work: UnitOfWork,
        table_name: str,
        read_schema: type[TReadSchema],
        db_create_schema: type[TDBCreateSchema],
        db_update_schema: type[TDBUpdateSchema],
    ) -> None:
        self._repository = repository
        self._uof = unit_of_work
        self._table_name = table_name
        self._read_schema = read_schema
        self._db_create_schema = db_create_schema
        self._db_update_schema = db_update_schema

    async def bulk_create(self, data: Iterable[TCreateSchema]) -> list[TReadSchema]:
        bulk_create_data = self._bulk_create_data_transfer(data)
        async with self._uof:
            return [
                self._read_schema.model_validate(obj)
                for obj in await self._repository.bulk_create(bulk_create_data)
            ]

    async def create(self, data: TCreateSchema) -> TReadSchema:
        create_data = self._create_data_transfer(data)
        async with self._uof:
            return self._read_schema.model_validate(
                await self._repository.create(create_data)
            )

    async def update(self, obj_id: int, data: TUpdateSchema) -> TReadSchema:
        update_data = self._update_data_transfer(data)
        async with self._uof:
            new_obj = await self._repository.update(obj_id, update_data)
            if not new_obj:
                raise ObjectNotFoundError(obj_id=obj_id, table_name=self._table_name)
            return self._read_schema.model_validate(new_obj)

    async def delete(self, obj_id: int) -> None:
        async with self._uof:
            if not await self._repository.delete(obj_id):
                raise ObjectNotFoundError(obj_id=obj_id, table_name=self._table_name)

    def _create_data_transfer(self, data: TCreateSchema) -> TDBCreateSchema:
        return self._db_create_schema(**data.model_dump())

    def _bulk_create_data_transfer(
        self, data: Iterable[TCreateSchema]
    ) -> list[TDBCreateSchema]:
        return [self._db_create_schema(**obj.model_dump()) for obj in data]

    def _update_data_transfer(self, data: TUpdateSchema) -> TDBUpdateSchema:
        return self._db_update_schema(**data.model_dump(exclude_unset=True))


class ServiceBase[
    TRepository: RepositoryBase[Any, Any, Any, Any],
    TReadSchema: BaseModel,
    TCreateSchema: BaseModel,
    TUpdateSchema: BaseModel,
    TDBCreateSchema: BaseModel,
    TDBUpdateSchema: BaseModel,
](
    QueryServiceBase[TRepository, TReadSchema],
    CommandServiceBase[
        TRepository,
        TReadSchema,
        TCreateSchema,
        TUpdateSchema,
        TDBCreateSchema,
        TDBUpdateSchema,
    ],
):
    def __init__(  # noqa: PLR0913
        self,
        repository: TRepository,
        unit_of_work: UnitOfWork,
        table_name: str,
        read_schema: type[TReadSchema],
        db_create_schema: type[TDBCreateSchema],
        db_update_schema: type[TDBUpdateSchema],
    ) -> None:
        QueryServiceBase.__init__(
            self, repository=repository, table_name=table_name, read_schema=read_schema
        )
        CommandServiceBase.__init__(
            self,
            repository=repository,
            unit_of_work=unit_of_work,
            table_name=table_name,
            read_schema=read_schema,
            db_create_schema=db_create_schema,
            db_update_schema=db_update_schema,
        )
