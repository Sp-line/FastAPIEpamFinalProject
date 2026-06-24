from dishka import Provider
from dishka import Scope
from dishka import provide

from app.usages.users.login import UserLoginUsage


class UsagesProvider(Provider):
    scope = Scope.REQUEST

    get_user_login_usage = provide(UserLoginUsage)
