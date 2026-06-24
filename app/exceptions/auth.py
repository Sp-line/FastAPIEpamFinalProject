class AuthError(Exception):
    pass


class InvalidCredentialsError(AuthError):
    pass
