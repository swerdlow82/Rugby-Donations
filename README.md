# Oregon Men's Rugby donations

University of Oregon Men's Rugby fundraising site:

- **Public site:** club info, photos, roster, and a GiveCampus donate button
- **Player accounts:** `@uoregon.edu` email confirmation required
- **Contact book:** 20 emails and 10 phone numbers per player
- **Outreach:** custom email (SendGrid) and SMS (Twilio) with `{donate_link}` pointing at GiveCampus
- **Gifts:** University of Oregon GiveCampus form (not processed on this site)

## Stack

| Layer | Choice |
| --- | --- |
| Frontend | Next.js |
| Backend | FastAPI |
| Database | AWS RDS PostgreSQL |
| Email | SendGrid |
| SMS | Twilio (SendGrid does not send texts) |
| Payments | GiveCampus (UO official form) |
| Deploy | Google Cloud Run (`cloudbuild.yaml`) |

## Local run

1. Copy `.env.example` to `.env` and fill secrets. RDS credentials can live in `RDS_DATABASE_URL`. If RDS is not reachable, run local Postgres on port 5433.
2. Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```

3. Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

Without SendGrid, signup returns a confirmation link on screen. Without Twilio, texts are logged by the API instead of sent. `{donate_link}` always uses `GIVECAMPUS_DONATE_URL`.

## Player flow

1. Sign up with `you@uoregon.edu`
2. Confirm the email link
3. Save up to 20 emails and 10 numbers (people who already agreed to hear from the player)
4. Send a custom ask using `{player_name}`, `{contact_name}`, `{donate_link}`
