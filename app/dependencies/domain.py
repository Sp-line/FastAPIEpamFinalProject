from dishka import Provider
from dishka import Scope
from dishka import provide

from app.domain.project import EnsureCanDeleteProject
from app.domain.project import EnsureCanRetrieveProject
from app.domain.project import EnsureCanUpdateProject


class DomainProvider(Provider):
    scope = Scope.APP

    get_ensure_can_delete_project = provide(EnsureCanDeleteProject)
    get_ensure_can_update_project = provide(EnsureCanUpdateProject)
    get_ensure_can_retrieve_project = provide(EnsureCanRetrieveProject)
