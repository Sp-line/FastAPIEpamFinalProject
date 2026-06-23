from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

from app.core.auth.password import PasswordService  # noqa: TC001
from app.repositories.unit_of_work import UnitOfWork  # noqa: TC001
from app.repositories.user import UserRepository
from app.schemas.user import UserCreateDB
from app.schemas.user import UserCreateReq
from app.schemas.user import UserRead
from app.schemas.user import UserUpdateDB
from app.schemas.user import UserUpdateReq
from app.services.base import ServiceBase


class UserService(
    ServiceBase[
        UserRepository,
        UserRead,
        UserCreateReq,
        UserUpdateReq,
        UserCreateDB,
        UserUpdateDB,
    ],
):
    def __init__(
        self,
        repository: UserRepository,
        unit_of_work: UnitOfWork,
        password_service: PasswordService,
    ) -> None:
        super().__init__(
            repository=repository,
            unit_of_work=unit_of_work,
            table_name="users",
            read_schema=UserRead,
            db_create_schema=UserCreateDB,
            db_update_schema=UserUpdateDB,
        )
        self._password_service = password_service

    def _create_data_transfer(self, data: UserCreateReq) -> UserCreateDB:
        hashed_password = self._password_service.get_password_hash(data.password)
        return UserCreateDB(username=data.username, hashed_password=hashed_password)

    def _update_data_transfer(self, data: UserUpdateReq) -> UserUpdateDB:
        updated_data = data.model_dump(exclude_unset=True, exclude={"password"})

        if data.password is not None:
            updated_data["hashed_password"] = self._password_service.get_password_hash(
                data.password
            )

        return UserUpdateDB(**updated_data)

    def _bulk_create_data_transfer(
        self, data: Iterable[UserCreateReq]
    ) -> list[UserCreateDB]:
        return [self._create_data_transfer(obj) for obj in data]
