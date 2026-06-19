#!/usr/bin/env python3
"""
Find OPL joiners and leavers from July 2024 - June 2025
Look through all sheets to find relevant data
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from datetime import datetime

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = '1-GEd1hIU7OOJ-CP97VqnrW1p0TPTXhzDAlgim08HLJM'

    try:
        # Get all sheets with their gid values
        metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = metadata.get('sheets', [])

        print("All sheets with gid values:")
        for sheet in sheets:
            title = sheet['properties']['title']
            gid = sheet['properties']['sheetId']
            print(f"  {title} (gid={gid})")

        # The user provided gid=81404103, let's find which sheet that is
        target_gid = 81404103
        target_sheet = None
        for sheet in sheets:
            if sheet['properties']['sheetId'] == target_gid:
                target_sheet = sheet['properties']['title']
                break

        print(f"\nSheet with gid={target_gid}: {target_sheet}")

        if target_sheet:
            print(f"\n{'='*80}")
            print(f"Reading data from sheet: {target_sheet}")
            print(f"{'='*80}\n")

            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{target_sheet}'!A1:Z100"
            ).execute()

            rows = result.get('values', [])
            print(f"First 50 rows:\n")
            for i, row in enumerate(rows[:50]):
                print(f"Row {i}: {row}")
        else:
            print(f"\nSheet with gid={target_gid} not found. Searching for audit-related sheets...")

            # Search for sheets that might have entity or joining/leaving data
            for sheet in sheets:
                title = sheet['properties']['title']
                if any(keyword in title.lower() for keyword in ['audit', 'entity', 'opl', 'joining', 'leaving', 'joiner', 'leaver']):
                    print(f"\n{'='*80}")
                    print(f"Found relevant sheet: {title}")
                    print(f"{'='*80}\n")

                    result = service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range=f"'{title}'!A1:Z100"
                    ).execute()

                    rows = result.get('values', [])
                    print(f"First 50 rows:\n")
                    for i, row in enumerate(rows[:50]):
                        print(f"Row {i}: {row}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
