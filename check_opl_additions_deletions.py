#!/usr/bin/env python3
"""Check the original audit sheet for OPL addition/deletion data"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            import json
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

creds = load_credentials()
service = build('sheets', 'v4', credentials=creds)

# Original audit sheet
spreadsheet_id = '1-GEd1hIU7OOJ-CP97VqnrW1p0TPTXhzDAlgim08HLJM'

try:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get('sheets', [])

    print("Sheets in audit file:")
    for sheet in sheets:
        title = sheet['properties']['title']
        gid = sheet['properties']['sheetId']
        print(f"  {title} (gid={gid})")

    # Check each sheet for OPL data
    for sheet in sheets:
        title = sheet['properties']['title']
        gid = sheet['properties']['sheetId']

        if 'opl' in title.lower() or 'opl' in title:
            print(f"\n{'='*150}")
            print(f"Found OPL sheet: {title} (gid={gid})")
            print(f"{'='*150}\n")

            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{title}'!A1:I50"
            ).execute()

            rows = result.get('values', [])
            for i, row in enumerate(rows[:50]):
                print(f"Row {i:2d}: {row}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
