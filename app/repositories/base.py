from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Sequence
    from typing import Any

    from app.app_types.map import IntMap
    from app.repositories.handlers.base import TableErrorHandler


class QueryRepositoryBase[
    TModel: IntIdPkMixin,
    TSession: AsyncSession = AsyncSession,
]:
    def __init__(self, model: type[TModel], session: TSession) -> None:
        self._model = model
        self._session = session

    async def get_by_ids(self, obj_ids: Iterable[int]) -> Sequence[TModel]:
        unique_ids = set(obj_ids)

        if not unique_ids:
            return []

        stmt = select(self._model).where(self._model.id.in_(unique_ids))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[TModel]:
        stmt = select(self._model).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, obj_id: int) -> TModel | None:
        return await self._session.get(self._model, obj_id)


class CommandRepositoryBase[
    TModel: IntIdPkMixin,
    TCreateSchema: BaseModel,
    TUpdateSchema: BaseModel,
    TSession: AsyncSession = AsyncSession,
]:
    def __init__(
        self,
        model: type[TModel],
        session: TSession,
        table_error_handler: TableErrorHandler,
    ) -> None:
        self._model = model
        self._session = session
        self._table_error_handler = table_error_handler

    async def create(self, data: TCreateSchema) -> TModel:
        obj = self._model(**data.model_dump())
        self._session.add(obj)

        try:
            await self._session.flush()
        except IntegrityError as e:
            self._table_error_handler.handle(e)
            raise

        await self._session.refresh(obj)
        return obj

    async def bulk_create(self, data: Iterable[TCreateSchema]) -> Sequence[TModel]:
        insert_data = [item.model_dump() for item in data]
        if not insert_data:
            return []

        stmt = insert(self._model).returning(self._model)

        try:
            result = await self._session.scalars(stmt, insert_data)
        except IntegrityError as e:
            self._table_error_handler.handle(e)
            raise

        return result.all()

    async def bulk_update(self, data: IntMap[TUpdateSchema]) -> Sequence[TModel]:
        if not data:
            return []

        update_data: list[dict[str, Any]] = []

        for obj_id, schema in data.items():
            data_dict = schema.model_dump(exclude_unset=True)
            if data_dict:
                data_dict["id"] = obj_id
                update_data.append(data_dict)

        if not update_data:
            return []

        stmt = update(self._model).returning(self._model)

        try:
            result = await self._session.scalars(stmt, update_data)
        except IntegrityError as e:
            self._table_error_handler.handle(e)
            raise

        return result.all()

    async def update(self, obj_id: int, data: TUpdateSchema) -> TModel | None:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self._session.get(self._model, obj_id)

        stmt = (
            update(self._model)
            .where(self._model.id == obj_id)
            .values(**update_data)
            .returning(self._model)
        )

        try:
            result = await self._session.execute(stmt)
        except IntegrityError as e:
            self._table_error_handler.handle(e)
            raise

        return result.scalar_one_or_none()

    async def delete(self, obj_id: int) -> bool:
        stmt = delete(self._model).where(self._model.id == obj_id)

        try:
            result = await self._session.execute(stmt)
        except IntegrityError as e:
            self._table_error_handler.handle(e)
            raise

        rowcount = int(getattr(result, "rowcount", 0))

        return rowcount > 0


class RepositoryBase[
    TModel: IntIdPkMixin,
    TCreateSchema: BaseModel,
    TUpdateSchema: BaseModel,
    TSession: AsyncSession = AsyncSession,
](
    QueryRepositoryBase[TModel, TSession],
    CommandRepositoryBase[TModel, TCreateSchema, TUpdateSchema, TSession],
):
    def __init__(
        self,
        model: type[TModel],
        session: TSession,
        table_error_handler: TableErrorHandler,
    ) -> None:
        QueryRepositoryBase.__init__(self, model=model, session=session)
        CommandRepositoryBase.__init__(
            self, model=model, session=session, table_error_handler=table_error_handler
        )
