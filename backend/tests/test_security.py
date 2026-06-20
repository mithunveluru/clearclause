import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("correct horse battery")
    assert h != "correct horse battery"
    assert verify_password("correct horse battery", h)
    assert not verify_password("wrong", h)


def test_access_token_roundtrip():
    token = create_access_token(42)
    assert decode_token(token, expected_type="access") == 42


def test_wrong_token_type_rejected():
    refresh = create_refresh_token(7)
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(refresh, expected_type="access")
