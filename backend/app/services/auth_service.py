from fastapi import HTTPException, status

from app.core import lockout
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    async def register(self, email: str, password: str) -> None:
        # Tells the caller the address is taken. That is enumerable, but the silent
        # no-op it replaces was worse: the client signs in straight after
        # registering, so a taken address produced "Invalid email or password" on
        # the signup screen. Enumeration is bounded by the 5/min limit on this route.
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
            # Counted against the account, not the IP — credential stuffing spreads
            # itself across IPs, which is exactly what the rate limiter cannot see.
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

    @staticmethod
    def _issue_tokens(user_id: int) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
