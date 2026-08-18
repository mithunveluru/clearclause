import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core import csrf, revocation
from app.core.config import settings
from app.core.ratelimit import rate_limit
from app.core.security import decode_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.repositories.document_repo import DocumentRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    AccountDeleteRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.account_service import AccountService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


REFRESH_PATH = "/api/v1/auth"  # refresh token travels only to refresh + logout


def _set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    """Write access + refresh tokens as httpOnly cookies, plus a readable CSRF token."""
    shared = {"samesite": settings.COOKIE_SAMESITE, "secure": settings.COOKIE_SECURE}
    response.set_cookie(
        "cc_token", tokens.access_token, max_age=1800, path="/", httponly=True, **shared
    )
    response.set_cookie(
        "cc_refresh",
        tokens.refresh_token,
        max_age=7 * 24 * 3600,
        path=REFRESH_PATH,
        httponly=True,
        **shared,
    )
    # Deliberately readable: the frontend echoes it back in a header
    response.set_cookie(
        csrf.COOKIE, csrf.new_token(), max_age=7 * 24 * 3600, path="/", httponly=False, **shared
    )


def _service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


def _account(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService(UserRepository(db), DocumentRepository(db))


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("cc_token", path="/")
    response.delete_cookie("cc_refresh", path=REFRESH_PATH)
    response.delete_cookie(csrf.COOKIE, path="/")


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
    _clear_auth_cookies(response)
    return {"ok": True}


@router.post(
    "/forgot-password",
    dependencies=[Depends(rate_limit(limit=5, window=60, scope="forgot"))],
)
async def forgot_password(body: PasswordResetRequest, svc: AuthService = Depends(_service)):
    """Mail a reset link to the address, if it has an account.

    Always 200, whether or not it does — a different response for a registered
    address would make this a free account enumerator.
    """
    await svc.request_password_reset(body.email)
    return {"ok": True}


@router.post(
    "/reset-password",
    dependencies=[Depends(rate_limit(limit=5, window=60, scope="reset"))],
)
async def reset_password(body: PasswordResetConfirm, svc: AuthService = Depends(_service)):
    """Set a new password from an emailed token. 400 if the link is spent or expired."""
    await svc.reset_password(body.token, body.password)
    return {"ok": True}


@router.get("/me/export")
async def export_account(
    user: User = Depends(get_current_user),
    svc: AccountService = Depends(_account),
):
    """Everything held about this account, as JSON."""
    return await svc.export(user)


@router.post("/me/delete", status_code=status.HTTP_200_OK)
async def delete_account(
    body: AccountDeleteRequest,
    response: Response,
    user: User = Depends(get_current_user),
    svc: AccountService = Depends(_account),
    cc_refresh: str | None = Cookie(default=None),
):
    """Erase the account, its documents, its files and its vectors. Irreversible.

    POST, not DELETE: it carries the password in a body, and a DELETE with a body is
    the kind of thing proxies and clients feel free to drop.
    """
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Password does not match"
        )
    await svc.delete(user)
    if cc_refresh is not None:
        try:
            await revocation.revoke(decode_token(cc_refresh, expected_type="refresh"))
        except (jwt.PyJWTError, revocation.RevocationUnavailable):
            pass  # the account is gone; the token now refreshes into nothing anyway
    _clear_auth_cookies(response)
    return {"ok": True}
