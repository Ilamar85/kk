"""Sends the generated digest by email (Markdown + rendered HTML)."""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown as markdown_lib

from pipeline.config import Config

logger = logging.getLogger(__name__)


def render_html(markdown_body: str) -> str:
    body_html = markdown_lib.markdown(markdown_body, extensions=["extra"])
    return f"<html><body>{body_html}</body></html>"


def send_email(config: Config, subject: str, markdown_body: str) -> None:
    required = [config.smtp_host, config.smtp_user, config.smtp_password, config.email_from, config.email_to]
    if not all(required):
        raise RuntimeError("Email delivery is not fully configured (SMTP_* / EMAIL_FROM / EMAIL_TO)")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = config.email_from
    message["To"] = ", ".join(config.email_to)
    message.attach(MIMEText(markdown_body, "plain", "utf-8"))
    message.attach(MIMEText(render_html(markdown_body), "html", "utf-8"))

    with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
        server.starttls()
        server.login(config.smtp_user, config.smtp_password)
        server.sendmail(config.email_from, config.email_to, message.as_string())

    logger.info("Digest email sent to %s", ", ".join(config.email_to))
