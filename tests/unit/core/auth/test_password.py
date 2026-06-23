import bcrypt
import pytest
from pydantic import SecretStr

from app.core.auth.password import PasswordService


def test_get_password_hash_returns_valid_bcrypt_string() -> None:
    raw_password = "SecurePassword123!"  # noqa: S105
    secret = SecretStr(raw_password)

    hashed_password = PasswordService.get_password_hash(secret)

    assert isinstance(hashed_password, str)
    assert hashed_password.startswith("$2")

    assert bcrypt.checkpw(raw_password.encode("utf-8"), hashed_password.encode("utf-8"))


def test_get_password_hash_generates_unique_hashes_for_same_password() -> None:
    secret = SecretStr("SamePassword123!")

    hash_1 = PasswordService.get_password_hash(secret)
    hash_2 = PasswordService.get_password_hash(secret)

    assert hash_1 != hash_2


def test_verify_password_returns_true_for_correct_password() -> None:
    secret = SecretStr("MySuperSecret99")
    valid_hash = PasswordService.get_password_hash(secret)

    is_valid = PasswordService.verify_password(secret, valid_hash)

    assert is_valid is True


@pytest.mark.parametrize(
    "wrong_password",
    [
        "mysupersecret99",
        "MySuperSecret99!",
        "WrongPassword",
        "",
    ],
    ids=[
        "case_sensitive_mismatch",
        "extra_character_mismatch",
        "completely_different_password",
        "empty_password",
    ],
)
def test_verify_password_returns_false_for_incorrect_password(
    wrong_password: str,
) -> None:
    correct_secret = SecretStr("MySuperSecret99")
    valid_hash = PasswordService.get_password_hash(correct_secret)
    wrong_secret = SecretStr(wrong_password)

    is_valid = PasswordService.verify_password(wrong_secret, valid_hash)

    assert is_valid is False


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "not_a_real_hash_string",
        "",
        "$2b$12$invalidhashthatisstilltoooshort",
    ],
    ids=[
        "random_text",
        "empty_string",
        "malformed_bcrypt_string",
    ],
)
def test_verify_password_raises_value_error_for_invalid_hash_format(
    invalid_hash: str,
) -> None:
    secret = SecretStr("AnyPassword123")

    with pytest.raises(ValueError, match="Invalid salt"):
        PasswordService.verify_password(secret, invalid_hash)
