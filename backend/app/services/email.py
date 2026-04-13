"""Email delivery service.

Uses Python stdlib smtplib/email — zero external dependencies.
When SMTP_HOST is not configured, emails are logged but not sent.
"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("agroveri.email")


def _is_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_from_email)


def _build_html(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;font-family:'Helvetica Neue',Arial,sans-serif;background:#F5F7F0">
<div style="max-width:520px;margin:30px auto;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #E8EBE5">
  <div style="background:#0A1F14;padding:24px 28px;text-align:center">
    <span style="font-size:20px;color:#fff;font-family:Georgia,serif">AgroVeri</span><span style="color:#C9A84C;font-size:20px;font-family:Georgia,serif">+</span>
  </div>
  <div style="padding:28px">
    <h2 style="margin:0 0 12px;font-size:20px;color:#0A1F14;font-family:Georgia,serif;font-weight:normal">{title}</h2>
    <p style="margin:0 0 20px;font-size:14px;color:#6B7C72;line-height:1.7">{body}</p>
    <hr style="border:none;border-top:1px solid #E8EBE5;margin:20px 0">
    <p style="margin:0;font-size:11px;color:#6B7C72;text-align:center">
      AgroVeri+ — Digital Traceability for Organic Agriculture
    </p>
  </div>
</div>
</body>
</html>"""


def _send_sync(to_email: str, subject: str, html_body: str) -> bool:
    """Send email synchronously (runs in thread pool)."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.ehlo()
            if settings.smtp_port == 587:
                server.starttls()
                server.ehlo()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False


async def send_email(to_email: str, subject: str, title: str, body: str) -> bool:
    """Send an HTML email asynchronously.

    Returns True if sent, False if failed or not configured.
    """
    if not _is_configured():
        logger.debug(f"Email skipped (SMTP not configured): {subject} → {to_email}")
        return False

    html = _build_html(title, body)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_sync, to_email, subject, html)


async def send_notification_email(to_email: str, title: str, body: str) -> bool:
    """Convenience wrapper: send a notification as email."""
    subject = f"AgroVeri+ — {title}"
    return await send_email(to_email, subject, title, body)
