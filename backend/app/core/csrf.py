"""Double-submit CSRF guard, needed once cookies go SameSite=None.

SameSite=Lax was doing this job for free: the browser withheld the auth cookie on
cross-site POSTs. Splitting the frontend (Vercel) from the API (Render) makes every
request cross-site, so the cookie must be SameSite=None — and with it, any page on
the internet can drive an authenticated state change unless something else proves
the request came from our own frontend.

The token is a random value in a readable (non-httpOnly) cookie. Our frontend echoes
it back in a header; an attacker's page can send the cookie but cannot read it to
build the header, and CORS refuses to let it read the response either.
"""
import secrets

from fastapi import HTTPException, Request, status

COOKIE = "cc_csrf"
HEADER = "X-CSRF-Token"

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
# No session exists yet so no token can be sent
# Both are rate limited and forging them gains nothing
_EXEMPT_PATHS = frozenset({"/api/v1/auth/login", "/api/v1/auth/register"})


def new_token() -> str:
    return secrets.token_urlsafe(32)


def enforce(request: Request) -> None:
    """Reject an unsafe request whose header does not match its CSRF cookie."""
    if request.method in _SAFE_METHODS or request.url.path in _EXEMPT_PATHS:
        return

    cookie = request.cookies.get(COOKIE, "")
    header = request.headers.get(HEADER, "")
    if not cookie or not secrets.compare_digest(cookie, header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token missing or invalid"
        )
