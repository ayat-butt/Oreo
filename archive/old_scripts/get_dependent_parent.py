#!/usr/bin/env python3
"""Get the parent employee for these dependents."""

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
    markaz_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get rows 545-555 to see the context
    result = service.spreadsheets().values().get(
        spreadsheetId=markaz_sheet_id,
        range='Sheet1!A545:D555'
    ).execute()

    values = result.get('values', [])

    print("Context around Beena Zahir and Zahir Ahmad:\n")
    print(f"{'Row':<6} {'Col A (ID)':<20} {'Col B (Employee)':<35} {'Col C (Dependent)':<35} {'Col D (Relation)':<20}")
    print("-" * 130)

    for idx, row in enumerate(values, start=545):
        col_a = row[0] if len(row) > 0 else ""
        col_b = row[1] if len(row) > 1 else ""
        col_c = row[2] if len(row) > 2 else ""
        col_d = row[3] if len(row) > 3 else ""

        # Truncate long names
        col_b_disp = (col_b[:35] if col_b else "")
        col_c_disp = (col_c[:35] if col_c else "")

        try:
            print(f"{idx:<6} {col_a:<20} {col_b_disp:<35} {col_c_disp:<35} {col_d:<20}")
        except:
            print(f"{idx:<6} {col_a:<20} [Non-ASCII] [Non-ASCII] {col_d:<20}")

if __name__ == "__main__":
    main()
