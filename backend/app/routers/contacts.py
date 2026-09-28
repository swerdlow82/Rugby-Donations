import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Contact, Player
from app.schemas import ContactBookIn, ContactBookOut, ContactOut
from app.security import require_verified

router = APIRouter(prefix="/contacts", tags=["contacts"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9\-\s()]{8,20}$")


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"[^\d+]", "", value.strip())
    if digits.startswith("+"):
        return "+" + re.sub(r"\D", "", digits)
    digits = re.sub(r"\D", "", digits)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}"


@router.get("", response_model=ContactBookOut)
def list_contacts(player: Player = Depends(require_verified), db: Session = Depends(get_db)):
    rows = db.query(Contact).filter(Contact.player_id == player.id).order_by(Contact.id).all()
    return ContactBookOut(
        emails=[ContactOut.model_validate(c) for c in rows if c.kind == "email"],
        phones=[ContactOut.model_validate(c) for c in rows if c.kind == "phone"],
    )


@router.put("", response_model=ContactBookOut)
def replace_contacts(
    payload: ContactBookIn,
    player: Player = Depends(require_verified),
    db: Session = Depends(get_db),
):
    if len(payload.emails) > 20:
        raise HTTPException(status_code=400, detail="You can save at most 20 emails.")
    if len(payload.phones) > 10:
        raise HTTPException(status_code=400, detail="You can save at most 10 phone numbers.")

    emails: list[tuple[str, str]] = []
    seen_email: set[str] = set()
    for item in payload.emails:
        value = item.value.strip().lower()
        if not value:
            continue
        if not EMAIL_RE.match(value):
            raise HTTPException(status_code=400, detail=f"Invalid email: {item.value}")
        if value in seen_email:
            continue
        seen_email.add(value)
        emails.append((item.name.strip(), value))

    phones: list[tuple[str, str]] = []
    seen_phone: set[str] = set()
    for item in payload.phones:
        raw = item.value.strip()
        if not raw:
            continue
        if not PHONE_RE.match(raw):
            raise HTTPException(status_code=400, detail=f"Invalid phone number: {item.value}")
        value = _normalize_phone(raw)
        if value in seen_phone:
            continue
        seen_phone.add(value)
        phones.append((item.name.strip(), value))

    db.query(Contact).filter(Contact.player_id == player.id).delete()
    for name, value in emails:
        db.add(Contact(player_id=player.id, kind="email", name=name, value=value))
    for name, value in phones:
        db.add(Contact(player_id=player.id, kind="phone", name=name, value=value))
    db.commit()
    return list_contacts(player, db)
