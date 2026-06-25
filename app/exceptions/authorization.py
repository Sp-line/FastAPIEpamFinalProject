class AuthorizationError(Exception):
    pass


class ForbiddenError(AuthorizationError):
    pass
