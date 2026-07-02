from app.constants.role_type import RoleType
from app.domain.base import EnsureHasRole


class EnsureCanDeleteDocument(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER}


class EnsureCanUpdateDocument(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER, RoleType.PARTICIPANT}


class EnsureCanRetrieveDocument(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER, RoleType.PARTICIPANT}


class EnsureCanCreateDocument(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER, RoleType.PARTICIPANT}


class EnsureCanListDocument(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER, RoleType.PARTICIPANT}
