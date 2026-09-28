import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str, text_body: str | None = None) -> None:
    if not settings.sendgrid_api_key:
        logger.info("SendGrid not configured. Would send to %s: %s\n%s", to_email, subject, text_body or html_body)
        return

    message = Mail(
        from_email=(settings.sendgrid_from_email, settings.sendgrid_from_name),
        to_emails=to_email,
        subject=subject,
        html_content=html_body,
        plain_text_content=text_body or html_body,
    )
    client = SendGridAPIClient(settings.sendgrid_api_key)
    response = client.send(message)
    if response.status_code >= 400:
        raise RuntimeError(f"SendGrid error {response.status_code}: {response.body}")
