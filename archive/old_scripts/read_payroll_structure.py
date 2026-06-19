#!/usr/bin/env python3
"""Read Payroll sheet structure to find bank details columns."""

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
    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'

    print("Reading OPL Payroll Sheet...\n")

    try:
        # Read from OPL sheet (gid=1424468564)
        result = service.spreadsheets().values().get(
            spreadsheetId=payroll_sheet_id,
            range="'OPL'!A1:Z50"
        ).execute()

        values = result.get('values', [])

        if values:
            headers = values[0]
            print(f"Column Headers ({len(headers)} columns):\n")
            for idx, header in enumerate(headers):
                print(f"  [{idx}] {header}")

            print("\n" + "="*150)
            print("\nSample Employee Record (Row 2):\n")
            if len(values) > 1:
                row = values[1]
                for idx, cell in enumerate(row[:20]):
                    if idx < len(headers):
                        print(f"  {headers[idx]}: {cell if cell else '[EMPTY]'}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
