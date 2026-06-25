class AuthenticationError(Exception):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class TokenExpiredError(AuthenticationError):
    pass


class TokenInvalidError(AuthenticationError):
    pass
