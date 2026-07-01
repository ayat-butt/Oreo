"""One-time helper: mint a read-only Gmail token for a mailbox (for offer-email ingestion).

Offer emails can land in EITHER ayat@niete.edu.pk OR ayat@taleemabad.com. The web backend
already has a token for the niete identity (GOOGLE_SERVICE_TOKEN_JSON); this script lets you
authorize the SECOND mailbox (ayat@taleemabad.com) for READ access.

Usage (run locally, you must be able to open a browser and sign in as that mailbox):

    python connect_mailbox.py taleemabad
    python connect_mailbox.py niete          # only if you want a dedicated niete read token

It uses the same credentials.json (Google OAuth client) the project already uses. After you
sign in and approve, it prints the token JSON. Copy it into Railway as an env var:

    taleemabad  ->  GMAIL_TOKEN_TALEEMABAD_JSON
    niete       ->  GMAIL_TOKEN_NIETE_JSON

Sign in as the matching account in the browser window that opens (NOT a different account).
"""

from __future__ import annotations

import sys

from google_auth_oauthlib.flow import InstalledAppFlow

from hr_assistant.config import GOOGLE_CREDENTIALS_FILE

# Read-only scopes the ingestion job needs: read mail, and read a linked JD Google Doc
# (documents/drive) that may be shared only within this mailbox's organization.
READ_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

ENV_VAR = {
    "taleemabad": "GMAIL_TOKEN_TALEEMABAD_JSON",
    "niete": "GMAIL_TOKEN_NIETE_JSON",
}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ENV_VAR:
        raise SystemExit("Usage: python connect_mailbox.py <taleemabad|niete>")
    which = sys.argv[1]

    flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, READ_SCOPES)
    creds = flow.run_local_server(port=0)
    token_json = creds.to_json()

    print("\n" + "=" * 72)
    print(f"  Token for '{which}' mailbox — set this Railway env var:")
    print(f"    {ENV_VAR[which]}")
    print("=" * 72)
    print(token_json)
    print("=" * 72)
    print("Paste the single-line JSON above as the env var value, then redeploy.\n")


if __name__ == "__main__":
    main()
