import jwt
import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

PROD = dict(
    ENV="production",
    JWT_SECRET="a-real-secret-value",
    COOKIE_SECURE=True,
    CORS_ORIGINS="https://clearclause.app",
)


def test_password_hash_roundtrip():
    h = hash_password("correct horse battery")
    assert h != "correct horse battery"
    assert verify_password("correct horse battery", h)
    assert not verify_password("wrong", h)


def test_access_token_roundtrip():
    token = create_access_token(42)
    payload = decode_token(token, expected_type="access")
    assert int(payload["sub"]) == 42
    assert payload["jti"]


def test_each_token_gets_a_unique_jti():
    a = decode_token(create_refresh_token(1), expected_type="refresh")
    b = decode_token(create_refresh_token(1), expected_type="refresh")
    assert a["jti"] != b["jti"]


def test_wrong_token_type_rejected():
    refresh = create_refresh_token(7)
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(refresh, expected_type="access")


def test_production_config_accepts_a_secure_deployment():
    assert Settings(**PROD).ENV == "production"


@pytest.mark.parametrize(
    "override",
    [
        {"JWT_SECRET": "change-me-in-prod"},   # default signing key
        {"COOKIE_SECURE": False},              # auth cookies without the Secure flag
        {"CORS_ORIGINS": "http://app.test"},   # plaintext origin
    ],
)
def test_production_refuses_to_start_insecure(override):
    # The dev defaults must never survive into production by omission.
    with pytest.raises(ValidationError):
        Settings(**{**PROD, **override})


def test_development_keeps_the_insecure_defaults():
    # Local dev over plain http must still work.
    assert Settings(ENV="development").COOKIE_SECURE is False
