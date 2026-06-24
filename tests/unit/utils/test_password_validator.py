import pytest
from pydantic import SecretStr

from app.constants.messages.auth import AuthErrorMessage
from app.utils.password_validator import validate_password_strength


@pytest.mark.parametrize(
    "raw_password",
    [
        "Valid123",
        "ComplexPass1!",
        "123StartsDigitUpperL",
        "lOwEr123",
    ],
    ids=[
        "standard_valid_password",
        "valid_with_special_characters",
        "starts_with_digit",
        "starts_with_lowercase",
    ],
)
def test_validate_password_strength_success(raw_password: str) -> None:
    secret = SecretStr(raw_password)

    result = validate_password_strength(secret)

    assert result.get_secret_value() == raw_password


@pytest.mark.parametrize(
    "raw_password",
    [
        "alllowercase",
        "ALLUPPERCASE",
        "1234567890",
        "OnlyLetters",
        "only123lower",
        "ONLY123UPPER",
        "!@#$%^&*()",
    ],
    ids=[
        "missing_upper_and_digit",
        "missing_lower_and_digit",
        "missing_letters_entirely",
        "missing_digit",
        "missing_upper",
        "missing_lower",
        "special_chars_only",
    ],
)
def test_validate_password_strength_raises_error(raw_password: str) -> None:
    secret = SecretStr(raw_password)

    with pytest.raises(ValueError, match=AuthErrorMessage.PASSWORD_TOO_WEAK) as exc_info:
        validate_password_strength(secret)

    assert str(exc_info.value) == AuthErrorMessage.PASSWORD_TOO_WEAK
