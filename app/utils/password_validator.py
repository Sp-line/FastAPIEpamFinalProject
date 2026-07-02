from __future__ import annotations

import re
from typing import TYPE_CHECKING

from app.constants.messages.authentication import AuthenticationErrorMessage
from app.constants.user import UserLimits

if TYPE_CHECKING:
    from pydantic import SecretStr


def validate_password_strength(value: SecretStr) -> SecretStr:
    raw_password = value.get_secret_value()
    if not re.match(UserLimits.PASSWORD_PATTERN, raw_password):
        raise ValueError(AuthenticationErrorMessage.PASSWORD_TOO_WEAK)
    return value
