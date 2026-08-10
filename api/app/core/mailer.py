import smtplib
from email.message import EmailMessage
from typing import Iterable

from app.core.config import config
from app.core.logger import logger


def _normalize_recipients(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


class Mailer:
    def send(
        self,
        to: str | Iterable[str],
        subject: str,
        body: str,
        cc: str | Iterable[str] | None = None,
    ) -> None:
        recipients = _normalize_recipients(to)
        cc_recipients = _normalize_recipients(cc)

        if not recipients:
            return

        if not config.SMTP_HOST:
            logger.info(
                "mail skipped",
                extra={
                    "reason": "smtp_not_configured",
                    "recipient_count": len(recipients),
                    "cc_count": len(cc_recipients),
                    "subject": subject,
                },
            )
            return

        message = EmailMessage()
        message["From"] = config.MAIL_FROM
        message["To"] = ", ".join(recipients)
        if cc_recipients:
            message["Cc"] = ", ".join(cc_recipients)
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            if config.SMTP_USE_TLS:
                server.starttls()
            if config.SMTP_USERNAME and config.SMTP_PASSWORD:
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(message)


def get_mailer() -> Mailer:
    return Mailer()
