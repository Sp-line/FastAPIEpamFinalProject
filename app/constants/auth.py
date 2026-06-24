from enum import StrEnum
from enum import auto


class JWTAlgorithm(StrEnum):
    @staticmethod
    def _generate_next_value_(
        name: str,
        _start: int,
        _count: int,
        _last_values: list[str],
    ) -> str:
        return name

    HS256 = auto()
    HS384 = auto()
    HS512 = auto()
    RS256 = auto()
