import logging
import re

# Keep PII and secrets out of stdout and Loki
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_TOKEN = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]+")


class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        msg = _EMAIL.sub("[email]", msg)
        msg = _TOKEN.sub(r"\1[redacted]", msg)
        record.msg = msg
        record.args = ()
        return True


def install_redaction() -> None:
    root = logging.getLogger()
    if not any(isinstance(f, RedactionFilter) for f in root.filters):
        root.addFilter(RedactionFilter())
    # Handlers filter propagated child records
    for handler in root.handlers:
        if not any(isinstance(f, RedactionFilter) for f in handler.filters):
            handler.addFilter(RedactionFilter())
