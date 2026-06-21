class UserLimits:
    USERNAME_MAX: int = 32
    USERNAME_MIN: int = 2

    PASSWORD_MIN: int = 8
    PASSWORD_MAX: int = 128
    PASSWORD_PATTERN: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$"

    HASHED_PASSWORD_MAX: int = 1024
    HASHED_PASSWORD_MIN: int = 50
