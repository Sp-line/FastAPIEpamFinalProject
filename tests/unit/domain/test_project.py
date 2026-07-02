from unittest.mock import MagicMock

import pytest

from app.constants.role_type import RoleType
from app.exceptions.authorization import ForbiddenError


@pytest.mark.parametrize(
    "policy_fixture_name",
    [
        "ensure_can_delete_project",
        "ensure_can_invite_user",
    ],
)
class TestOwnerOnlyProjectPolicies:
    def test_policy_executes_silently_for_owner(
        self,
        request: pytest.FixtureRequest,
        policy_fixture_name: str,
    ) -> None:
        policy = request.getfixturevalue(policy_fixture_name)

        result = policy(RoleType.OWNER)

        assert result is None

    @pytest.mark.parametrize(
        "invalid_role",
        [
            RoleType.PARTICIPANT,
            None,
            MagicMock(spec=RoleType),
        ],
        ids=["participant_role", "none_role", "unknown_mock_role"],
    )
    def test_policy_raises_forbidden_error_for_disallowed_roles(
        self,
        request: pytest.FixtureRequest,
        policy_fixture_name: str,
        invalid_role: RoleType | None,
    ) -> None:
        policy = request.getfixturevalue(policy_fixture_name)

        with pytest.raises(ForbiddenError):
            policy(invalid_role)


@pytest.mark.parametrize(
    "policy_fixture_name",
    [
        "ensure_can_retrieve_project",
        "ensure_can_update_project",
    ],
)
class TestSharedProjectPolicies:
    @pytest.mark.parametrize(
        "valid_role",
        [
            RoleType.OWNER,
            RoleType.PARTICIPANT,
        ],
        ids=["owner_role", "participant_role"],
    )
    def test_policy_executes_silently_for_allowed_roles(
        self,
        request: pytest.FixtureRequest,
        policy_fixture_name: str,
        valid_role: RoleType,
    ) -> None:
        policy = request.getfixturevalue(policy_fixture_name)

        result = policy(valid_role)

        assert result is None

    @pytest.mark.parametrize(
        "invalid_role",
        [
            None,
            MagicMock(spec=RoleType),
        ],
        ids=["none_role", "unknown_mock_role"],
    )
    def test_policy_raises_forbidden_error_for_disallowed_roles(
        self,
        request: pytest.FixtureRequest,
        policy_fixture_name: str,
        invalid_role: RoleType | None,
    ) -> None:
        policy = request.getfixturevalue(policy_fixture_name)

        with pytest.raises(ForbiddenError):
            policy(invalid_role)
