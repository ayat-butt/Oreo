#!/usr/bin/env python3
"""
Quick script to regenerate token.json for ayat@niete.edu.pk
Run: python regenerate_token.py
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

# Scopes for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

def regenerate_token():
    """Regenerate token.json using credentials.json"""

    cred_file = 'credentials.json'
    token_file = 'token.json'

    print("=" * 60)
    print("REGENERATING TOKEN.JSON")
    print("=" * 60)
    print()
    print("Account: ayat@niete.edu.pk")
    print("Credentials file: credentials.json")
    print()

    # Create flow from credentials
    flow = InstalledAppFlow.from_client_secrets_file(
        cred_file,
        SCOPES,
        redirect_uri='http://localhost'
    )

    print("Opening browser for OAuth login...")
    print("(If browser doesn't open, visit the URL printed below)")
    print()

    # Run local server for OAuth
    creds = flow.run_local_server(port=0)

    # Save token
    import json
    with open(token_file, 'w') as token:
        json.dump(creds.to_json(), token, indent=2)

    print()
    print("=" * 60)
    print("SUCCESS! token.json created")
    print("=" * 60)
    print()
    print("Account: ayat@niete.edu.pk")
    print("Token saved to: token.json")
    print()
    print("You can now access:")
    print("  - Gmail API")
    print("  - Google Calendar API")
    print("  - Google Drive API")
    print("  - Google Sheets API")
    print()

if __name__ == '__main__':
    try:
        regenerate_token()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
