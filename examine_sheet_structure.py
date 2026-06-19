#!/usr/bin/env python3
"""
Examine the actual sheet structure to understand the data format
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = '1-GEd1hIU7OOJ-CP97VqnrW1p0TPTXhzDAlgim08HLJM'

    try:
        # Check the "Total" sheet more carefully
        print("="*80)
        print("EXAMINING 'Total' SHEET STRUCTURE")
        print("="*80)

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="'Total'!A1:Z30"
        ).execute()

        rows = result.get('values', [])
        print(f"\nFirst 30 rows of 'Total' sheet:\n")
        for i, row in enumerate(rows[:30]):
            print(f"Row {i}: {row}")

        # Also check one of the month sheets
        print("\n" + "="*80)
        print("EXAMINING 'May 2025' SHEET STRUCTURE")
        print("="*80)

        result = service.spreadsheets().values().get(
            spreadsheet_id=spreadsheet_id,
            range="'May 2025'!A1:Z20"
        ).execute()

        rows = result.get('values', [])
        print(f"\nFirst 20 rows of 'May 2025' sheet:\n")
        for i, row in enumerate(rows[:20]):
            print(f"Row {i}: {row}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
