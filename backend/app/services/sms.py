import logging

from twilio.rest import Client

from app.config import settings

logger = logging.getLogger(__name__)


def send_sms(to_number: str, body: str) -> None:
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.info("Twilio not configured. Would SMS %s: %s", to_number, body)
        return

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    client.messages.create(
        body=body,
        from_=settings.twilio_from_number,
        to=to_number,
    )
