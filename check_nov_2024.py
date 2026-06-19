#!/usr/bin/env python3
"""Check November 2024 payroll sheet structure"""

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
    except:
        return None

creds = load_credentials()
service = build('sheets', 'v4', credentials=creds)

# November 2024 sheet
spreadsheet_id = '1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA'

try:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get('sheets', [])

    print(f"November 2024 sheet structure")
    for sheet in sheets:
        print(f"  - {sheet['properties']['title']}")

    # Get first data sheet
    target_sheet = sheets[0]['properties']['title']

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{target_sheet}'!A1:P50"
    ).execute()

    rows = result.get('values', [])
    print(f"\n\nSheet: {target_sheet}")
    print("="*180)
    for i, row in enumerate(rows[:50]):
        print(f"Row {i:2d}: {row}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
