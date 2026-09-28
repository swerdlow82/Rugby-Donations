from sqlalchemy.orm import Session

from app.models import TeamInfo, TeamPhoto


DEFAULT_PHOTOS = [
    {
        "title": "Match day",
        "image_url": "https://images.unsplash.com/photo-1546519638-68e109498ffc?auto=format&fit=crop&w=1600&q=80",
        "caption": "Oregon Men's Rugby competing in the Pacific Northwest.",
        "sort_order": 1,
    },
    {
        "title": "Scrum",
        "image_url": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?auto=format&fit=crop&w=1600&q=80",
        "caption": "Pack work, fitness, and togetherness define the club.",
        "sort_order": 2,
    },
    {
        "title": "Team",
        "image_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba6851?auto=format&fit=crop&w=1600&q=80",
        "caption": "Student-athletes representing the University of Oregon.",
        "sort_order": 3,
    },
]

BODY = """University of Oregon Men's Rugby is a student-run club competing across the Pacific Northwest. Your gift helps cover travel to conference matches, pitch and referee fees, kit, and training so players can keep the program on the field.

Gifts are processed by the University of Oregon through GiveCampus so they can be handled for tax purposes. Players still reach family and friends they already know by email and text, and every ask sends people to the official UO rugby designation.

Go Ducks."""


def seed_content(db: Session) -> None:
    info = db.query(TeamInfo).first()
    if not info:
        db.add(
            TeamInfo(
                headline="University of Oregon Men's Rugby",
                body=BODY,
            )
        )
    elif "Stripe" in info.body:
        info.body = BODY
    if not db.query(TeamPhoto).first():
        for photo in DEFAULT_PHOTOS:
            db.add(TeamPhoto(**photo))
    db.commit()
