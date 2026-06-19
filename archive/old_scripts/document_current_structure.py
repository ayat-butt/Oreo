#!/usr/bin/env python3
"""Document the exact current structure of the Insurance sheet."""

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

    print("Reading current Insurance sheet structure...\n")

    try:
        # Get headers
        result = service.spreadsheets().values().get(
            spreadsheetId=insurance_sheet_id,
            range='Sheet1!1:1'
        ).execute()

        headers = result.get('values', [[]])[0]

        print("=" * 150)
        print("CURRENT SHEET STRUCTURE - BASELINE VERSION")
        print("=" * 150)
        print("\nColumn Headers:\n")

        for idx, header in enumerate(headers):
            col_letter = chr(65 + idx)  # A, B, C, D, etc.
            print(f"  [{col_letter}] Column {idx}: {header}")

        # Show sample row
        print("\n" + "=" * 150)
        print("Sample Employee Record (Row 2):\n")

        result = service.spreadsheets().values().get(
            spreadsheetId=insurance_sheet_id,
            range='Sheet1!A2:Z2'
        ).execute()

        sample_row = result.get('values', [[]])[0] if result.get('values') else []

        for idx, cell in enumerate(sample_row):
            col_letter = chr(65 + idx)
            print(f"  [{col_letter}] {headers[idx] if idx < len(headers) else f'Column {idx}'}: {cell if cell else '[EMPTY]'}")

        print("\n" + "=" * 150)
        print("BASELINE SAVED - This is the CLEAN version before bank details")
        print("=" * 150)
        print("\nNow you can tell me:")
        print("  1. Which column (A, B, C, D, etc.) to add Bank Name after?")
        print("  2. Should Account Number be in the next column?")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
