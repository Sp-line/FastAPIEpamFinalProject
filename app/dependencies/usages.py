from dishka import Provider
from dishka import Scope
from dishka import provide

from app.usages.documents.create import DocumentCreateUsage
from app.usages.documents.delete import DocumentDeleteUsage
from app.usages.documents.list import DocumentListUsage
from app.usages.documents.retrieve import DocumentRetrieveUsage
from app.usages.documents.update import DocumentUpdateUsage
from app.usages.projects.create import ProjectCreateUsage
from app.usages.projects.delete import ProjectDeleteUsage
from app.usages.projects.list import ProjectListInfoUsage
from app.usages.projects.retrieve import ProjectRetrieveInfoUsage
from app.usages.projects.update import ProjectUpdateUsage
from app.usages.users.login import UserLoginUsage


class UsagesProvider(Provider):
    scope = Scope.REQUEST

    get_user_login_usage = provide(UserLoginUsage)

    get_project_create_usage = provide(ProjectCreateUsage)
    get_project_delete_usage = provide(ProjectDeleteUsage)
    get_project_update_usage = provide(ProjectUpdateUsage)
    get_project_retrieve_info_usage = provide(ProjectRetrieveInfoUsage)
    get_project_list_info_usage = provide(ProjectListInfoUsage)

    get_document_create_usage = provide(DocumentCreateUsage)
    get_document_delete_usage = provide(DocumentDeleteUsage)
    get_document_retrieve_usage = provide(DocumentRetrieveUsage)
    get_document_list_usage = provide(DocumentListUsage)
    get_document_update_usage = provide(DocumentUpdateUsage)
