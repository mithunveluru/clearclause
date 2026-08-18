import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TTL = timedelta(minutes=30)
REFRESH_TTL = timedelta(days=7)
RESET_TTL = timedelta(minutes=30)


def hash_password(password: str) -> str:
    # bcrypt errors past 72 bytes
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode()[:72], password_hash.encode())


def _make_token(subject: str, token_type: str, ttl: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + ttl,
        "jti": uuid.uuid4().hex,  # revocable individually
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _make_token(str(user_id), "access", ACCESS_TTL)


def create_refresh_token(user_id: int) -> str:
    return _make_token(str(user_id), "refresh", REFRESH_TTL)


def decode_token(token: str, expected_type: str) -> dict:
    """Return the token payload, or raise jwt exceptions on invalid/expired/wrong-type."""
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("wrong token type")
    return payload


def _reset_key(password_hash: str) -> str:
    """Reset tokens are signed with the password they are about to replace.

    Single use and one-outstanding-token come free: completing a reset changes the
    hash, so every token issued against the old one stops verifying. No table, no
    Redis round trip, and no window where a Redis outage lets a spent link work.
    """
    return settings.JWT_SECRET + password_hash


def create_reset_token(user_id: int, password_hash: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "reset",
        "iat": now,
        "exp": now + RESET_TTL,
    }
    return jwt.encode(payload, _reset_key(password_hash), algorithm=ALGORITHM)


def reset_token_subject(token: str) -> int:
    """The user id a reset token claims, read *without* verifying the signature.

    Only safe use is loading that user's password hash to verify against — which is
    the chicken-and-egg the hash-bound key creates. Never trust it for anything else.
    """
    payload = jwt.decode(token, options={"verify_signature": False})
    return int(payload["sub"])


def decode_reset_token(token: str, password_hash: str) -> dict:
    """Return the payload, or raise jwt exceptions on invalid/expired/spent/wrong-type."""
    payload = jwt.decode(token, _reset_key(password_hash), algorithms=[ALGORITHM])
    if payload.get("type") != "reset":
        raise jwt.InvalidTokenError("wrong token type")
    return payload
