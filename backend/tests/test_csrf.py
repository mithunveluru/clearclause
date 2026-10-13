"""The double-submit guard that replaces SameSite=Lax on a split-domain deploy."""
import pytest
from fastapi import HTTPException

from app.core import csrf


class _Req:
    def __init__(self, method="POST", path="/api/v1/documents/upload", cookies=None, headers=None):
        self.method = method
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.url = type("U", (), {"path": path})()


def test_matching_cookie_and_header_passes():
    token = csrf.new_token()
    csrf.enforce(_Req(cookies={csrf.COOKIE: token}, headers={csrf.HEADER: token}))


def test_missing_header_is_rejected():
    # Attacker sends the cookie but cannot read it
    with pytest.raises(HTTPException) as e:
        csrf.enforce(_Req(cookies={csrf.COOKIE: csrf.new_token()}))
    assert e.value.status_code == 403


def test_mismatched_header_is_rejected():
    with pytest.raises(HTTPException):
        csrf.enforce(
            _Req(cookies={csrf.COOKIE: csrf.new_token()}, headers={csrf.HEADER: csrf.new_token()})
        )


def test_no_cookie_is_rejected():
    with pytest.raises(HTTPException):
        csrf.enforce(_Req(headers={csrf.HEADER: csrf.new_token()}))


def test_reads_are_not_guarded():
    csrf.enforce(_Req(method="GET", path="/api/v1/documents"))


def test_login_and_register_are_exempt():
    # No session yet so no token to echo
    csrf.enforce(_Req(path="/api/v1/auth/login"))
    csrf.enforce(_Req(path="/api/v1/auth/register"))
