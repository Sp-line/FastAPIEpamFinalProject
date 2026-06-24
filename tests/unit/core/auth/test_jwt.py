from datetime import UTC
from datetime import datetime

import jwt
import pytest
from pydantic import SecretStr

from app.constants.auth import JWTAlgorithm
from app.core.auth.jwt import JWTService
from app.schemas.token import JWTPayload


@pytest.fixture
def jwt_service() -> JWTService:
    return JWTService(
        secret=SecretStr("super_secret_test_key_for_jwt_123"),
        algorithm=JWTAlgorithm.HS256,
        lifetime_seconds=3600,
    )


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
