from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from app.core.models.user import User
from app.repositories.base import RepositoryBase
from app.repositories.handlers.user import users_error_handler
from app.schemas.user import UserCreateDB
from app.schemas.user import UserUpdateDB


class UserRepository(
    RepositoryBase[
        User,
        UserCreateDB,
        UserUpdateDB,
    ]
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            model=User,
            session=session,
            table_error_handler=users_error_handler,
        )
