from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING

import jwt
import pytest

if TYPE_CHECKING:
    from app.core.auth.jwt import JWTService
from app.exceptions.auth import TokenExpiredError
from app.exceptions.auth import TokenInvalidError
from app.schemas.token import JWTPayload


@pytest.mark.parametrize(
    ("custom_lifetime", "expected_lifetime_seconds"),
    [
        (None, 3600),
        (1800, 1800),
    ],
    ids=[
        "default_lifetime",
        "custom_lifetime",
    ],
)
def test_create_access_token_encodes_payload_and_sets_exp(
    jwt_service: JWTService,
    custom_lifetime: int | None,
    expected_lifetime_seconds: int,
) -> None:
    user_id = "user_123"
    payload = JWTPayload(sub=user_id)
    time_before_creation = datetime.now(UTC).timestamp()

    token = jwt_service.create_access_token(
        payload=payload,
        lifetime_seconds=custom_lifetime,
    )

    decoded_payload = jwt.decode(
        jwt=token,
        key=jwt_service.secret.get_secret_value(),
        algorithms=[jwt_service.algorithm],
    )

    assert decoded_payload["sub"] == user_id
    assert "exp" in decoded_payload

    expected_exp = time_before_creation + expected_lifetime_seconds
    time_tolerance_seconds = 2

    assert abs(decoded_payload["exp"] - expected_exp) <= time_tolerance_seconds


@pytest.mark.parametrize(
    "lifetime_seconds",
    [0, -60],
    ids=["zero_lifetime", "negative_lifetime"],
)
def test_create_access_token_creates_expired_token(
    jwt_service: JWTService,
    lifetime_seconds: int,
) -> None:
    payload = JWTPayload(sub="user_123")

    token = jwt_service.create_access_token(
        payload=payload,
        lifetime_seconds=lifetime_seconds,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            jwt=token,
            key=jwt_service.secret.get_secret_value(),
            algorithms=[jwt_service.algorithm],
        )


def test_create_access_token_mutates_payload_object(jwt_service: JWTService) -> None:
    payload = JWTPayload(sub="user_123")

    jwt_service.create_access_token(payload=payload)

    assert payload.exp is not None
    assert isinstance(payload.exp, datetime)


def test_create_access_token_uses_correct_algorithm_header(
    jwt_service: JWTService,
) -> None:
    payload = JWTPayload(sub="user_123")

    token = jwt_service.create_access_token(payload=payload)

    header = jwt.get_unverified_header(token)
    assert header["alg"] == jwt_service.algorithm.value
    assert header["typ"] == "JWT"


def test_verify_access_token_returns_payload_on_valid_token(
    jwt_service: JWTService,
    valid_payload: JWTPayload,
) -> None:
    token = jwt_service.create_access_token(valid_payload)

    result = jwt_service.verify_access_token(token)

    assert isinstance(result, JWTPayload)
    assert result.sub == "42"


def test_verify_access_token_raises_expired_error_on_expired_token(
    jwt_service: JWTService,
    valid_payload: JWTPayload,
) -> None:
    token = jwt_service.create_access_token(valid_payload, lifetime_seconds=-10)

    with pytest.raises(TokenExpiredError):
        jwt_service.verify_access_token(token)


def test_verify_access_token_raises_invalid_error_on_tampered_signature(
    jwt_service: JWTService,
    valid_payload: JWTPayload,
) -> None:
    valid_token = jwt_service.create_access_token(valid_payload)

    header, payload, signature = valid_token.split(".")

    bad_token = f"{header}.{payload}.{signature}invalid"

    with pytest.raises(TokenInvalidError):
        jwt_service.verify_access_token(bad_token)


def test_verify_access_token_raises_invalid_error_on_wrong_secret(
    jwt_service: JWTService,
) -> None:
    bad_token = jwt.encode(
        payload={"sub": "42"},
        key="completely_wrong_secret_key_for_this_test",
        algorithm=jwt_service.algorithm.value,
    )

    with pytest.raises(TokenInvalidError):
        jwt_service.verify_access_token(bad_token)


def test_verify_access_token_raises_invalid_error_on_wrong_algorithm(
    jwt_service: JWTService,
    jwt_secret: str,
) -> None:
    bad_token = jwt.encode(
        payload={"sub": "42"},
        key=jwt_secret,
        algorithm="HS512",
    )

    with pytest.raises(TokenInvalidError):
        jwt_service.verify_access_token(bad_token)


def test_verify_access_token_raises_invalid_error_on_missing_sub_claim(
    jwt_service: JWTService,
    jwt_secret: str,
) -> None:
    bad_token = jwt.encode(
        payload={"role": "admin", "username": "hacker"},
        key=jwt_secret,
        algorithm=jwt_service.algorithm.value,
    )

    with pytest.raises(TokenInvalidError):
        jwt_service.verify_access_token(bad_token)


def test_verify_access_token_raises_invalid_error_on_malformed_string(
    jwt_service: JWTService,
) -> None:
    bad_token = "not.a_real.jwt_token"  # noqa: S105

    with pytest.raises(TokenInvalidError):
        jwt_service.verify_access_token(bad_token)
