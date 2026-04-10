"""Configuration — Google + Microsoft Teams auth setup."""

import os
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


def get_google_services():
    """Authenticate and return Gmail, Calendar, and Drive service clients."""
    creds = None

    if Path(GOOGLE_TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(GOOGLE_CREDENTIALS_FILE).exists():
                raise FileNotFoundError(
                    f"Google credentials file '{GOOGLE_CREDENTIALS_FILE}' not found.\n"
                    "Download it from Google Cloud Console > APIs & Services > Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(GOOGLE_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return {
        "gmail": build("gmail", "v1", credentials=creds),
        "calendar": build("calendar", "v3", credentials=creds),
        "drive": build("drive", "v3", credentials=creds),
        "docs": build("docs", "v1", credentials=creds),
        "sheets": build("sheets", "v4", credentials=creds),
    }
