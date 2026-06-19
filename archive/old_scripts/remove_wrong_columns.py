#!/usr/bin/env python3
"""Remove the incorrectly added bank detail columns E and F."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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

    service = build('sheets', 'v4', credentials=creds)
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    print("Removing incorrect bank detail columns (E & F)...\n")

    try:
        # Get sheet ID for Sheet1
        metadata = service.spreadsheets().get(spreadsheetId=insurance_sheet_id).execute()
        sheet_id = None
        for sheet in metadata['sheets']:
            if sheet['properties']['title'] == 'Sheet1':
                sheet_id = sheet['properties']['sheetId']
                break

        if sheet_id is None:
            print("[ERROR] Could not find Sheet1")
            return

        # Delete columns E and F (index 4 and 5)
        requests = [
            {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 4,  # Column E (0-indexed)
                        'endIndex': 6     # Up to but not including column G
                    }
                }
            }
        ]

        response = service.spreadsheets().batchUpdate(
            spreadsheetId=insurance_sheet_id,
            body={'requests': requests}
        ).execute()

        print("[OK] Deleted columns E and F (Bank Name and Account Number)")
        print("[OK] Sheet restored to original state\n")

        print("Insurance sheet is now clean - ready for correct bank details placement!")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
