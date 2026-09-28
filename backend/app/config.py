from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    database_url: str = "postgresql://rugby:rugby@localhost:5432/rugby_donations"
    db_user: str | None = None
    db_password: str | None = None
    db_name: str | None = None
    db_host: str | None = None
    db_port: int = 5432

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    allowed_email_domain: str = "uoregon.edu"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"

    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "oregonrugby@example.com"
    sendgrid_from_name: str = "Oregon Men's Rugby"

    # SendGrid does not send SMS. Twilio is used for texts.
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    givecampus_donate_url: str = (
        "https://www.givecampus.com/campaigns/67036/donations/new?designation_id=5396121"
    )
    campaign_title: str = "Oregon Men's Rugby 2026 Season"

    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://") and "sslmode=" not in url:
            if "rds.amazonaws.com" in url:
                url = url + ("&" if "?" in url else "?") + "sslmode=require"
        if url.count("/") == 2 or url.rstrip("/").endswith("amazonaws.com"):
            # host only, no database name
            if self.db_name and f"/{self.db_name}" not in url.split("?")[0]:
                base, *query = url.split("?", 1)
                url = f"{base.rstrip('/')}/{self.db_name}"
                if query:
                    url += f"?{query[0]}"
        return url


settings = Settings()
