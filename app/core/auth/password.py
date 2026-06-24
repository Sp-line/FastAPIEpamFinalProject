from __future__ import annotations

from typing import TYPE_CHECKING

import bcrypt

if TYPE_CHECKING:
    from pydantic import SecretStr


class PasswordService:
    @staticmethod
    def verify_password(password: SecretStr, hashed_password: str) -> bool:
        password_bytes = password.get_secret_value().encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    @staticmethod
    def get_password_hash(password: SecretStr) -> str:
        password_bytes = password.get_secret_value().encode("utf-8")
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed_bytes.decode("utf-8")
