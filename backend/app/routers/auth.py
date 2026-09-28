from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import EmailVerification, Player
from app.schemas import LoginRequest, PlayerOut, SignupRequest, TokenResponse
from app.security import create_access_token, get_current_player, hash_password, verify_password
from app.services.email import send_email


class SignupResponse(PlayerOut):
    verification_hint: str | None = None

router = APIRouter(prefix="/auth", tags=["auth"])


def _assert_uo_email(email: str) -> str:
    normalized = email.strip().lower()
    domain = settings.allowed_email_domain.lower()
    if not normalized.endswith(f"@{domain}"):
        raise HTTPException(
            status_code=400,
            detail=f"Player accounts must use a @{domain} address.",
        )
    return normalized


def _send_verification(player: Player, token: str) -> None:
    link = f"{settings.frontend_url}/verify?token={token}"
    send_email(
        player.email,
        "Confirm your Oregon Rugby player account",
        f"""
        <p>Hi {player.full_name},</p>
        <p>Confirm your University of Oregon email to finish setting up your rugby fundraising account.</p>
        <p><a href="{link}">Confirm my @uoregon.edu account</a></p>
        <p>This link expires in 24 hours.</p>
        """,
        f"Confirm your account: {link}",
    )


@router.post("/signup", response_model=SignupResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    email = _assert_uo_email(payload.email)
    if db.query(Player).filter(Player.email == email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    player = Player(
        email=email,
        full_name=payload.full_name.strip(),
        jersey_number=payload.jersey_number,
        position=payload.position,
        hashed_password=hash_password(payload.password),
        is_verified=False,
    )
    db.add(player)
    db.flush()

    token = secrets.token_urlsafe(32)
    db.add(
        EmailVerification(
            player_id=player.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
    )
    db.commit()
    db.refresh(player)
    _send_verification(player, token)
    hint = None
    if not settings.sendgrid_api_key:
        hint = f"{settings.frontend_url}/verify?token={token}"
    return SignupResponse.model_validate(player).model_copy(update={"verification_hint": hint})


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    player = db.query(Player).filter(Player.email == email).first()
    if not player or not verify_password(payload.password, player.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not player.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Check your Duck ID inbox and confirm your @uoregon.edu email before logging in.",
        )
    return TokenResponse(access_token=create_access_token(player.id))


@router.post("/verify/{token}", response_model=TokenResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    record = db.query(EmailVerification).filter(EmailVerification.token == token).first()
    if not record or record.used:
        raise HTTPException(status_code=400, detail="This confirmation link is invalid.")
    if record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This confirmation link has expired.")

    player = db.get(Player, record.player_id)
    if not player:
        raise HTTPException(status_code=400, detail="Account not found.")
    player.is_verified = True
    record.used = True
    db.commit()
    return TokenResponse(access_token=create_access_token(player.id))


@router.post("/resend-verification")
def resend(payload: LoginRequest, db: Session = Depends(get_db)):
    email = _assert_uo_email(payload.email)
    player = db.query(Player).filter(Player.email == email).first()
    if not player or not verify_password(payload.password, player.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if player.is_verified:
        return {"ok": True, "message": "Already verified."}

    token = secrets.token_urlsafe(32)
    db.add(
        EmailVerification(
            player_id=player.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
    )
    db.commit()
    _send_verification(player, token)
    return {"ok": True}


@router.get("/me", response_model=PlayerOut)
def me(player: Player = Depends(get_current_player)):
    return player
