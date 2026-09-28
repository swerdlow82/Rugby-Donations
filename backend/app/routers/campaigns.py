from datetime import datetime, timezone
from html import escape

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Contact, OutreachCampaign, OutreachMessage, Player
from app.schemas import CampaignIn, CampaignOut
from app.security import require_verified
from app.services.email import send_email
from app.services.sms import send_sms

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _personalize(template: str, player: Player, contact: Contact) -> str:
    donate = settings.givecampus_donate_url
    return (
        template.replace("{player_name}", player.full_name)
        .replace("{contact_name}", contact.name or "friend")
        .replace("{donate_link}", donate)
        .replace("{jersey}", player.jersey_number or "")
    )


@router.get("", response_model=list[CampaignOut])
def list_campaigns(player: Player = Depends(require_verified), db: Session = Depends(get_db)):
    campaigns = (
        db.query(OutreachCampaign)
        .filter(OutreachCampaign.player_id == player.id)
        .order_by(OutreachCampaign.id.desc())
        .all()
    )
    return [_summarize(db, c) for c in campaigns]


@router.post("", response_model=CampaignOut)
def create_and_send(
    payload: CampaignIn,
    player: Player = Depends(require_verified),
    db: Session = Depends(get_db),
):
    if not payload.send_email and not payload.send_sms:
        raise HTTPException(status_code=400, detail="Choose email, text, or both.")

    contacts = db.query(Contact).filter(Contact.player_id == player.id).all()
    emails = [c for c in contacts if c.kind == "email"]
    phones = [c for c in contacts if c.kind == "phone"]
    if payload.send_email and not emails:
        raise HTTPException(status_code=400, detail="Add emails in your contact book first.")
    if payload.send_sms and not phones:
        raise HTTPException(status_code=400, detail="Add phone numbers in your contact book first.")

    campaign = OutreachCampaign(
        player_id=player.id,
        subject=payload.subject,
        email_body=payload.email_body,
        sms_body=payload.sms_body,
        send_email=payload.send_email,
        send_sms=payload.send_sms,
    )
    db.add(campaign)
    db.flush()

    targets: list[tuple[Contact, str]] = []
    if payload.send_email:
        targets.extend((c, "email") for c in emails)
    if payload.send_sms:
        targets.extend((c, "sms") for c in phones)

    for contact, channel in targets:
        message = OutreachMessage(
            campaign_id=campaign.id,
            contact_id=contact.id,
            channel=channel,
            status="queued",
        )
        db.add(message)
        db.flush()
        try:
            if channel == "email":
                body = _personalize(payload.email_body, player, contact)
                html = f"<p>{escape(body).replace(chr(10), '<br/>')}</p>"
                send_email(contact.value, payload.subject, html, body)
            else:
                send_sms(contact.value, _personalize(payload.sms_body, player, contact))
            message.status = "sent"
            message.sent_at = datetime.now(timezone.utc)
        except Exception as exc:  # noqa: BLE001
            message.status = "failed"
            message.error = str(exc)[:2000]

    db.commit()
    db.refresh(campaign)
    return _summarize(db, campaign)


def _summarize(db: Session, campaign: OutreachCampaign) -> CampaignOut:
    messages = db.query(OutreachMessage).filter(OutreachMessage.campaign_id == campaign.id).all()
    return CampaignOut(
        id=campaign.id,
        subject=campaign.subject,
        created_at=campaign.created_at,
        emails_queued=sum(1 for m in messages if m.channel == "email"),
        sms_queued=sum(1 for m in messages if m.channel == "sms"),
        emails_sent=sum(1 for m in messages if m.channel == "email" and m.status == "sent"),
        sms_sent=sum(1 for m in messages if m.channel == "sms" and m.status == "sent"),
        failed=sum(1 for m in messages if m.status == "failed"),
    )
