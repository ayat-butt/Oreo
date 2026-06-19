#!/usr/bin/env python3
"""Debug - show what's actually in main sheet column A."""

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
    print("Reading Main Sheet Column A (first 20 rows)...\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!A1:A50'
        ).execute()

        values = result.get('values', [])

        print("Row | Content")
        print("-" * 100)

        for idx, row in enumerate(values, 1):
            if row:
                content = row[0] if row else "[EMPTY]"
                print(f"{idx:3} | {content}")
            else:
                print(f"{idx:3} | [EMPTY]")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
