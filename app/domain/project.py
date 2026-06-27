from app.constants.role_type import RoleType
from app.domain.base import EnsureHasRole


class EnsureCanDeleteProject(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER}


class EnsureCanRetrieveProject(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER, RoleType.PARTICIPANT}


class EnsureCanUpdateProject(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER, RoleType.PARTICIPANT}
