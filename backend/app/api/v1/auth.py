import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import revocation
from app.core.config import settings
from app.core.ratelimit import rate_limit
from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


REFRESH_PATH = "/api/v1/auth"  # refresh token travels only to refresh + logout


def _set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    """Write access + refresh tokens as httpOnly cookies."""
    shared = {"httponly": True, "samesite": "lax", "secure": settings.COOKIE_SECURE}
    response.set_cookie("cc_token", tokens.access_token, max_age=1800, path="/", **shared)
    response.set_cookie(
        "cc_refresh",
        tokens.refresh_token,
        max_age=7 * 24 * 3600,
        path=REFRESH_PATH,
        **shared,
    )


def _service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(limit=5, window=60, scope="register"))],
)
async def register(body: RegisterRequest, svc: AuthService = Depends(_service)):
    await svc.register(body.email, body.password)  # 409 if the address is taken
    return {"ok": True}


@router.post(
    "/login",
    dependencies=[Depends(rate_limit(limit=10, window=60, scope="login"))],
)
async def login(
    body: LoginRequest,
    response: Response,
    svc: AuthService = Depends(_service),
):
    tokens = await svc.login(body.email, body.password)
    _set_auth_cookies(response, tokens)
    return {"ok": True}


@router.post(
    "/refresh",
    dependencies=[Depends(rate_limit(limit=5, window=60, scope="refresh"))],
)
async def refresh(
    response: Response,
    cc_refresh: str | None = Cookie(default=None),
    svc: AuthService = Depends(_service),
):
    """Issue a new access + refresh token pair from the httpOnly refresh cookie.

    Rotates: the presented refresh token is revoked, so it cannot be replayed.
    """
    if cc_refresh is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    try:
        payload = decode_token(cc_refresh, expected_type="refresh")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    try:
        if await revocation.is_revoked(payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is no longer valid"
            )
        tokens = await svc.refresh(int(payload["sub"]))
        await revocation.revoke(payload)
    except revocation.RevocationUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not verify session; please sign in again.",
        )

    _set_auth_cookies(response, tokens)
    return {"ok": True}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, cc_refresh: str | None = Cookie(default=None)):
    """Revoke the refresh token, then clear both cookies.

    Without the revoke, logout only dropped the client's copy — a stolen token
    stayed valid for its full 7 days.
    """
    if cc_refresh is not None:
        try:
            await revocation.revoke(decode_token(cc_refresh, expected_type="refresh"))
        except (jwt.PyJWTError, revocation.RevocationUnavailable):
            pass  # already invalid, or Redis is down — still clear the cookies below
    response.delete_cookie("cc_token", path="/")
    response.delete_cookie("cc_refresh", path=REFRESH_PATH)
    return {"ok": True}
