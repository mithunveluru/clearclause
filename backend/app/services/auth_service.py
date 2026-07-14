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

    @staticmethod
    def _issue_tokens(user_id: int) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
