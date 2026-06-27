from dishka import Provider
from dishka import Scope
from dishka import provide

from app.usages.projects.create import ProjectCreateUsage
from app.usages.projects.delete import ProjectDeleteUsage
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
