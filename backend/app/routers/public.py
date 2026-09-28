from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Player, TeamInfo, TeamPhoto
from app.schemas import PhotoOut, PlayerOut, TeamPage

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/team", response_model=TeamPage)
def team_page(db: Session = Depends(get_db)):
    info = db.query(TeamInfo).order_by(TeamInfo.id).first()
    photos = db.query(TeamPhoto).order_by(TeamPhoto.sort_order, TeamPhoto.id).all()
    players = (
        db.query(Player)
        .filter(Player.is_verified.is_(True))
        .order_by(Player.full_name)
        .all()
    )
    return TeamPage(
        headline=info.headline if info else "University of Oregon Men's Rugby",
        body=info.body if info else "Support the Ducks on and off the pitch.",
        donate_url=settings.givecampus_donate_url,
        photos=[PhotoOut.model_validate(p) for p in photos],
        players=[PlayerOut.model_validate(p) for p in players],
    )
