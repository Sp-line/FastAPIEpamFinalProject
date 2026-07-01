from unittest.mock import MagicMock

import pytest

from app.constants.role_type import RoleType
from app.domain.document import EnsureCanCreateDocument
from app.domain.document import EnsureCanDeleteDocument
from app.domain.document import EnsureCanListDocument
from app.domain.document import EnsureCanRetrieveDocument
from app.domain.document import EnsureCanUpdateDocument
from app.domain.project import EnsureCanDeleteProject
from app.domain.project import EnsureCanInviteUser
from app.domain.project import EnsureCanRetrieveProject
from app.domain.project import EnsureCanUpdateProject


@pytest.fixture
def ensure_can_delete_project() -> EnsureCanDeleteProject:
    return EnsureCanDeleteProject()


@pytest.fixture
def ensure_can_invite_user() -> EnsureCanInviteUser:
    return EnsureCanInviteUser()


@pytest.fixture
def ensure_can_retrieve_project() -> EnsureCanRetrieveProject:
    return EnsureCanRetrieveProject()


@pytest.fixture
def ensure_can_update_project() -> EnsureCanUpdateProject:
    return EnsureCanUpdateProject()


@pytest.fixture
def ensure_can_delete_document() -> EnsureCanDeleteDocument:
    return EnsureCanDeleteDocument()


@pytest.fixture
def ensure_can_update_document() -> EnsureCanUpdateDocument:
    return EnsureCanUpdateDocument()


@pytest.fixture
def ensure_can_retrieve_document() -> EnsureCanRetrieveDocument:
    return EnsureCanRetrieveDocument()


@pytest.fixture
def ensure_can_create_document() -> EnsureCanCreateDocument:
    return EnsureCanCreateDocument()


@pytest.fixture
def ensure_can_list_document() -> EnsureCanListDocument:
    return EnsureCanListDocument()


@pytest.fixture
def mock_ensure_can_delete_project() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_ensure_can_update_project() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_ensure_can_retrieve_project() -> MagicMock:
    mock = MagicMock()
    mock.allowed_roles = {RoleType.OWNER, RoleType.PARTICIPANT}
    return mock


@pytest.fixture
def mock_ensure_can_invite_user() -> MagicMock:
    return MagicMock()
