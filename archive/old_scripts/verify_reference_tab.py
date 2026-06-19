#!/usr/bin/env python3
"""Verify what's now in the reference tab after update."""

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
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get reference tab data
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="'Data from Old Insurance Sheet'!A:J"
    ).execute()

    values = result.get('values', [])
    print(f"\nReference Tab - 11 Missing Employees:\n")
    print(f"{'Name':<40} {'CNIC':<20} {'Entity':<20}")
    print("-" * 80)

    for idx, row in enumerate(values[1:]):  # Skip header
        if row and row[0]:
            name = row[0][:40]
            cnic = row[1] if len(row) > 1 else ""
            try:
                print(f"{name:<40} {cnic:<20}")
            except:
                pass

if __name__ == "__main__":
    main()
