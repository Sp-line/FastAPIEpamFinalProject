from unittest.mock import MagicMock

import pytest

from app.constants.role_type import RoleType
from app.domain.base import EnsureHasRole
from app.exceptions.authorization import ForbiddenError


class ConcreteEnsureHasRole(EnsureHasRole):
    @property
    def allowed_roles(self) -> set[RoleType]:
        return {RoleType.OWNER, RoleType.PARTICIPANT}


@pytest.fixture
def ensure_has_role_policy() -> ConcreteEnsureHasRole:
    return ConcreteEnsureHasRole()


@pytest.mark.parametrize(
    "valid_role",
    [
        RoleType.OWNER,
        RoleType.PARTICIPANT,
    ],
    ids=["role_owner", "role_participant"],
)
def test_call_executes_silently_for_allowed_roles(
    ensure_has_role_policy: ConcreteEnsureHasRole,
    valid_role: RoleType,
) -> None:
    ensure_has_role_policy(valid_role)


def test_call_raises_forbidden_error_for_disallowed_role(
    ensure_has_role_policy: ConcreteEnsureHasRole,
) -> None:
    disallowed_role = MagicMock(spec=RoleType)

    with pytest.raises(ForbiddenError):
        ensure_has_role_policy(disallowed_role)


def test_call_raises_forbidden_error_when_role_is_none(
    ensure_has_role_policy: ConcreteEnsureHasRole,
) -> None:
    with pytest.raises(ForbiddenError):
        ensure_has_role_policy(None)
