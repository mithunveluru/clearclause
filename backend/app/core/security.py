import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TTL = timedelta(minutes=30)
REFRESH_TTL = timedelta(days=7)


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
