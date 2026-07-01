import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.ratelimit import rate_limit
from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    """Write access + refresh tokens as httpOnly cookies."""
    shared = {"httponly": True, "samesite": "lax", "secure": settings.COOKIE_SECURE}
    response.set_cookie("cc_token", tokens.access_token, max_age=1800, path="/", **shared)
    response.set_cookie(
        "cc_refresh",
        tokens.refresh_token,
        max_age=7 * 24 * 3600,
        path="/api/v1/auth/refresh",  # refresh token only travels to this endpoint
        **shared,
    )


def _service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(limit=5, window=60, scope="register"))],
)
async def register(body: RegisterRequest, svc: AuthService = Depends(_service)):
    return await svc.register(body.email, body.password)


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
    """Issue a new access + refresh token pair from the httpOnly refresh cookie."""
    if cc_refresh is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    try:
        user_id = decode_token(cc_refresh, expected_type="refresh")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    tokens = await svc.refresh(user_id)
    _set_auth_cookies(response, tokens)
    return {"ok": True}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie("cc_token", path="/")
    response.delete_cookie("cc_refresh", path="/api/v1/auth/refresh")
    return {"ok": True}
