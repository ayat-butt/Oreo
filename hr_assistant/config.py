"""Configuration — Google + Microsoft Teams auth setup."""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Google
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

# Microsoft Teams
TEAMS_CLIENT_ID = os.getenv("TEAMS_CLIENT_ID", "")
TEAMS_CLIENT_SECRET = os.getenv("TEAMS_CLIENT_SECRET", "")
TEAMS_TENANT_ID = os.getenv("TEAMS_TENANT_ID", "")
TEAMS_TOKEN_FILE = os.getenv("TEAMS_TOKEN_FILE", "teams_token.json")
TEAMS_SCOPES = [
    "https://graph.microsoft.com/Chat.ReadWrite",
    "https://graph.microsoft.com/ChannelMessage.Send",
    "https://graph.microsoft.com/Calendars.ReadWrite",
    "https://graph.microsoft.com/User.Read",
]

# General
HR_MANAGER_EMAIL = os.getenv("HR_MANAGER_EMAIL", "")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Our Company")

# Markaz HRMS
MARKAZ_BASE_URL = os.getenv("MARKAZ_BASE_URL", "https://markaz.taleemabad.com")
MARKAZ_EMAIL = os.getenv("MARKAZ_EMAIL", "")
MARKAZ_PASSWORD = os.getenv("MARKAZ_PASSWORD", "")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]

HR_LABELS = ["HR/Contracts", "HR/Benefits", "HR/Payroll", "HR/Employee-Queries"]

CATEGORY_KEYWORDS = {
    "HR/Contracts": [
        "contract", "agreement", "offer letter", "employment", "nda",
        "sign", "onboarding", "new hire", "terms",
    ],
    "HR/Benefits": [
        "benefit", "health insurance", "dental", "vision", "401k",
        "retirement", "pto", "vacation", "leave", "wellness",
    ],
    "HR/Payroll": [
        "payroll", "salary", "pay", "paycheck", "direct deposit",
        "tax", "w2", "compensation", "bonus", "raise",
    ],
    "HR/Employee-Queries": [
        "question", "query", "help", "policy", "procedure", "hr",
        "request", "complaint", "feedback", "concern",
    ],
}


def load_credentials(allow_interactive: bool = True) -> Credentials:
    """Resolve Google credentials for the service identity (ayat@niete.edu.pk).

    Resolution order:
      1. env GOOGLE_SERVICE_TOKEN_JSON  → web/Railway path (no disk writes; FS is ephemeral)
      2. token.json on disk             → CLI path (refreshed token persisted back to disk)
      3. interactive OAuth (CLI only)   → only if allow_interactive=True

    The web backend calls this with allow_interactive=False so it can never block on a
    browser flow; it must have GOOGLE_SERVICE_TOKEN_JSON or a valid token.json.
    """
    creds = None
    from_env = False

    env_blob = os.getenv("GOOGLE_SERVICE_TOKEN_JSON")
    if env_blob:
        creds = Credentials.from_authorized_user_info(json.loads(env_blob))
        from_env = True
    elif Path(GOOGLE_TOKEN_FILE).exists():
        # Load with the token's own granted scopes (not SCOPES) so refreshes never fail
        # with invalid_scope when SCOPES later gains a scope the saved token never had.
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif allow_interactive:
            if not Path(GOOGLE_CREDENTIALS_FILE).exists():
                raise FileNotFoundError(
                    f"Google credentials file '{GOOGLE_CREDENTIALS_FILE}' not found.\n"
                    "Download it from Google Cloud Console > APIs & Services > Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            raise RuntimeError(
                "No valid Google credentials and interactive auth is disabled (web context). "
                "Set GOOGLE_SERVICE_TOKEN_JSON or provide a refreshable token.json."
            )
        # Persist only when using the on-disk token (never write back in the web/env path).
        if not from_env:
            with open(GOOGLE_TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

    return creds


def get_google_services(allow_interactive: bool = True):
    """Authenticate and return Gmail, Calendar, Drive, Docs, Sheets service clients.

    CLI scripts call this with no args (interactive allowed). The web backend passes
    allow_interactive=False. cache_discovery=False avoids file-cache writes on read-only/ephemeral FS.
    """
    creds = load_credentials(allow_interactive=allow_interactive)
    return {
        "gmail": build("gmail", "v1", credentials=creds, cache_discovery=False),
        "calendar": build("calendar", "v3", credentials=creds, cache_discovery=False),
        "drive": build("drive", "v3", credentials=creds, cache_discovery=False),
        "docs": build("docs", "v1", credentials=creds, cache_discovery=False),
        "sheets": build("sheets", "v4", credentials=creds, cache_discovery=False),
    }
