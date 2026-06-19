#!/usr/bin/env python3
"""Restore Insurance sheet to previous version (before bank details were added)."""

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

    print("Attempting to restore Insurance sheet...\n")
    print("Checking revision history...\n")

    try:
        # Get file revisions
        drive_service = build('drive', 'v3', credentials=creds)
        revisions = drive_service.revisions().list(
            fileId=insurance_sheet_id,
            fields='revisions(id,modifiedTime,keepForever)',
            pageSize=10
        ).execute()

        revisions_list = revisions.get('revisions', [])
        print(f"Found {len(revisions_list)} revisions:\n")

        for idx, rev in enumerate(revisions_list):
            print(f"{idx}: {rev['modifiedTime']} (ID: {rev['id']})")

        if len(revisions_list) > 1:
            print(f"\nRevisions are available. Please:")
            print(f"1. Go to https://docs.google.com/spreadsheets/d/{insurance_sheet_id}/edit")
            print(f"2. Click Version history (top right)")
            print(f"3. Select a version BEFORE the latest update")
            print(f"\nOr I can help you manually restore if you provide the correct column structure.")
        else:
            print("\nLimited revision history available.")

    except Exception as e:
        print(f"Error accessing revisions: {e}")
        print("\nPlease restore using Google Sheets version history:")
        print(f"1. Open: https://docs.google.com/spreadsheets/d/{insurance_sheet_id}/edit")
        print(f"2. Click 'Version history' (clock icon, top right)")
        print(f"3. Select version before the bank details were added")
        print(f"4. Click 'Restore this version'")

if __name__ == "__main__":
    main()
