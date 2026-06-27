import pytest

from app.domain.project import EnsureCanDeleteProject
from app.domain.project import EnsureCanRetrieveProject
from app.domain.project import EnsureCanUpdateProject


@pytest.fixture
def ensure_can_delete_project() -> EnsureCanDeleteProject:
    return EnsureCanDeleteProject()


@pytest.fixture
def ensure_can_update_project() -> EnsureCanUpdateProject:
    return EnsureCanUpdateProject()


@pytest.fixture
def ensure_can_retrieve_project() -> EnsureCanRetrieveProject:
    return EnsureCanRetrieveProject()
