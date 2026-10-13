"""Transactional email over SMTP.

stdlib smtplib, no provider SDK: Resend, SES, Postmark and Mailgun all speak SMTP,
so switching provider is a config change rather than a code change.

A blank SMTP_HOST logs the message instead of sending it — what development and CI
want. Production cannot start with it blank (see Settings), because a password reset
that silently mails nothing strands the user with no error to report.
"""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

# A hung SMTP server must not hold a worker process indefinitely
TIMEOUT = 10


def send(to: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST:
        logger.info("email not sent (no SMTP_HOST): to=%s subject=%s", to, subject)
        return

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=TIMEOUT) as smtp:
        # ponytail: STARTTLS on 587. Add implicit TLS (SMTP_SSL, port 465) when a
        # provider that only offers it turns up.
        smtp.starttls()
        if settings.SMTP_USER:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(message)
    logger.info("sent %r to %s", subject, to)
