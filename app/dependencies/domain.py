from dishka import Provider
from dishka import Scope
from dishka import provide

from app.domain.document import EnsureCanCreateDocument
from app.domain.document import EnsureCanDeleteDocument
from app.domain.document import EnsureCanListDocument
from app.domain.document import EnsureCanRetrieveDocument
from app.domain.document import EnsureCanUpdateDocument
from app.domain.project import EnsureCanDeleteProject
from app.domain.project import EnsureCanInviteUser
from app.domain.project import EnsureCanRetrieveProject
from app.domain.project import EnsureCanUpdateProject


class DomainProvider(Provider):
    scope = Scope.APP

    get_ensure_can_delete_project = provide(EnsureCanDeleteProject)
    get_ensure_can_update_project = provide(EnsureCanUpdateProject)
    get_ensure_can_retrieve_project = provide(EnsureCanRetrieveProject)
    get_ensure_can_invite_user = provide(EnsureCanInviteUser)

    get_ensure_can_delete_document = provide(EnsureCanDeleteDocument)
    get_ensure_can_update_document = provide(EnsureCanUpdateDocument)
    get_ensure_can_retrieve_document = provide(EnsureCanRetrieveDocument)
    get_ensure_can_list_document = provide(EnsureCanListDocument)
    get_ensure_can_create_document = provide(EnsureCanCreateDocument)
