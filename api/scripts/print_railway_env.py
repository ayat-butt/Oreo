"""Print the Railway env block for the backend.

Run LOCALLY:  python -m api.scripts.print_railway_env
Then copy the output into Railway → your service → Variables → "Raw Editor".
Fill the 4 PASTE_* / YOUR-* placeholders (Google client id/secret + your deployed URLs).

This reads secrets from your local .env and token.json — they are printed to YOUR terminal only.
The script itself contains no secrets (safe to commit).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def env_val(key: str) -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith(key + "="):
            return line[len(key) + 1:]
    return ""


token = json.dumps(json.load(open(ROOT / "token.json", encoding="utf-8")))

block = f"""ENVIRONMENT=production
JWT_SECRET={env_val('JWT_SECRET')}
ALLOWLIST_EMAILS={env_val('ALLOWLIST_EMAILS')}
TEST_PILOT_EMAIL={env_val('TEST_PILOT_EMAIL')}
MARKAZ_DB_URL={env_val('MARKAZ_DB_URL')}
APP_DATABASE_URL={env_val('APP_DATABASE_URL')}
GOOGLE_SERVICE_TOKEN_JSON={token}
GOOGLE_OAUTH_CLIENT_ID=PASTE_FROM_GOOGLE
GOOGLE_OAUTH_CLIENT_SECRET=PASTE_FROM_GOOGLE
OAUTH_REDIRECT_URI=https://YOUR-RAILWAY-URL/auth/callback
FRONTEND_URL=https://YOUR-VERCEL-URL
CORS_ALLOWED_ORIGINS=https://YOUR-VERCEL-URL"""

print(block)
