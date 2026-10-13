import jwt
from fastapi import HTTPException, status

from app.core import lockout
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_reset_token,
    hash_password,
    reset_token_subject,
    verify_password,
)
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse

RESET_SUBJECT = "Reset your ClearClause password"
RESET_BODY = """\
Someone asked to reset the password for this ClearClause account.

Open this link within 30 minutes to choose a new one:

{link}

If that wasn't you, ignore this email — your password has not changed.
"""


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    async def register(self, email: str, password: str) -> None:
        # Enumerable, but bounded by the 5/min limit
        if await self.users.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
        await self.users.create(email, hash_password(password))

    async def login(self, email: str, password: str) -> TokenResponse:
        if await lockout.is_locked(email):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed sign-in attempts. Try again in 15 minutes.",
            )
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            # Per-account: credential stuffing spreads across IPs
            await lockout.record_failure(email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        await lockout.clear(email)
        return self._issue_tokens(user.id)

    async def refresh(self, user_id: int) -> TokenResponse:
        if not await self.users.get_by_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user"
            )
        return self._issue_tokens(user_id)

    async def request_password_reset(self, email: str) -> None:
        """Mail a reset link, if the address belongs to an account.

        Returns the same way either way: answering differently for a registered and
        an unregistered address turns this endpoint into an account enumerator.
        """
        user = await self.users.get_by_email(email)
        if user is None:
            return
        token = create_reset_token(user.id, user.password_hash)
        link = f"{settings.PUBLIC_APP_URL}/reset-password?token={token}"
        # Imported here: the API process should not pull in the worker at module load
        from app.worker.tasks import send_email

        send_email.delay(user.email, RESET_SUBJECT, RESET_BODY.format(link=link))

    async def reset_password(self, token: str, new_password: str) -> None:
        """Set a new password from a reset token, or 400 if the link is no good.

        One error for every failure mode — expired, forged, already used, unknown
        user — because the differences are only useful to someone guessing.
        """
        invalid = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link is invalid or has expired. Request a new one.",
        )
        try:
            user = await self.users.get_by_id(reset_token_subject(token))
            if user is None:
                raise invalid
            decode_reset_token(token, user.password_hash)
        except (jwt.PyJWTError, KeyError, ValueError):
            raise invalid

        await self.users.set_password(user, hash_password(new_password))
        # The lockout is keyed to failed guesses at the password that just changed
        await lockout.clear(user.email)

    @staticmethod
    def _issue_tokens(user_id: int) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
