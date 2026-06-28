class EmailServiceError(Exception):
    pass


class MissingEmailContentError(EmailServiceError):
    pass
