#!/usr/bin/env python3
"""Restore sheet from previous revision."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from io import BytesIO

def load_google_credentials():
    token_path = 'c:/Agent Oreo/token.json'
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    creds = load_google_credentials()
    if not creds:
        return

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    print("Restoring Insurance sheet from previous version...\n")

    try:
        # Get revision 47 (before the bank update)
        # Create a copy from revision 47
        file_metadata = {
            'name': 'Insurance - Recovery Version',
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }

        # Download revision
        request = drive_service.revisions().get_media(
            fileId=insurance_sheet_id,
            revisionId='47'
        )

        print("Manual Restoration Instructions:")
        print("=" * 100)
        print("\nTo restore the Insurance sheet from version history:")
        print("\n1. Open the sheet: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")
        print("\n2. Click the 'Version history' button (clock icon at top right)")
        print("\n3. Look for version from approximately 07:34 (ID: 47)")
        print("\n4. Click on that version to preview it")
        print("\n5. Click 'Restore this version' button")
        print("\n6. Confirm the restoration")
        print("\n" + "=" * 100)
        print("\nThis will restore your sheet to the state BEFORE the bank columns were added.")

    except Exception as e:
        print(f"Note: {e}")
        print("\nPlease use Google Sheets' native version history:")
        print("1. Open: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")
        print("2. Top right: Click clock icon (Version history)")
        print("3. Select version from ~07:34")
        print("4. Click 'Restore this version'")

if __name__ == "__main__":
    main()
