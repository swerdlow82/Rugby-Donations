from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    jersey_number: str | None = Field(default=None, max_length=8)
    position: str | None = Field(default=None, max_length=40)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PlayerOut(BaseModel):
    id: int
    email: str
    full_name: str
    jersey_number: str | None
    position: str | None
    is_verified: bool

    model_config = {"from_attributes": True}


class ContactIn(BaseModel):
    name: str = Field(default="", max_length=120)
    value: str = Field(min_length=3, max_length=255)


class ContactOut(BaseModel):
    id: int
    kind: str
    name: str
    value: str

    model_config = {"from_attributes": True}


class ContactBookIn(BaseModel):
    emails: list[ContactIn] = Field(default_factory=list, max_length=20)
    phones: list[ContactIn] = Field(default_factory=list, max_length=10)


class ContactBookOut(BaseModel):
    emails: list[ContactOut]
    phones: list[ContactOut]


class CampaignIn(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    email_body: str = Field(min_length=10, max_length=8000)
    sms_body: str = Field(min_length=10, max_length=320)
    send_email: bool = True
    send_sms: bool = True
    confirmed_consent: bool = False

    @field_validator("confirmed_consent")
    @classmethod
    def require_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "Confirm that these people know you and agreed to receive fundraising messages."
            )
        return v


class CampaignOut(BaseModel):
    id: int
    subject: str
    created_at: datetime
    emails_queued: int
    sms_queued: int
    emails_sent: int
    sms_sent: int
    failed: int


class PhotoOut(BaseModel):
    id: int
    title: str
    image_url: str
    caption: str

    model_config = {"from_attributes": True}


class TeamPage(BaseModel):
    headline: str
    body: str
    donate_url: str
    photos: list[PhotoOut]
    players: list[PlayerOut]
