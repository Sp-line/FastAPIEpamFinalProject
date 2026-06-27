from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.constants.role_type import RoleType

from app.constants.messages.authorization import AuthorizationErrorMessage
from app.exceptions.authorization import ForbiddenError


class EnsureHasRole(ABC):
    @property
    @abstractmethod
    def allowed_roles(self) -> set[RoleType]: ...

    def __call__(self, role: RoleType | None) -> None:
        if role is None or role not in self.allowed_roles:
            raise ForbiddenError(AuthorizationErrorMessage.FORBIDDEN)
