import logging

from app.core.logredact import RedactionFilter


def _record(msg: str) -> logging.LogRecord:
    return logging.LogRecord("t", logging.INFO, "x", 1, msg, (), None)


def test_redacts_email_and_bearer_token():
    rec = _record("login a@b.com with Authorization: Bearer abc.def-123 done")
    RedactionFilter().filter(rec)
    out = rec.getMessage()
    assert "a@b.com" not in out and "[email]" in out
    assert "abc.def-123" not in out and "[redacted]" in out


def test_plain_message_untouched():
    rec = _record("processing document 42")
    RedactionFilter().filter(rec)
    assert rec.getMessage() == "processing document 42"
