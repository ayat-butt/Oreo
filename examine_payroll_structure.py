#!/usr/bin/env python3
"""Examine payroll sheet structure to understand OPL data"""

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

# Main payroll sheet (July 2024 - June 2025)
spreadsheet_id = '1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k'

try:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get('sheets', [])

    print("Sheets in comprehensive payroll:")
    for sheet in sheets:
        print(f"  - {sheet['properties']['title']}")

    # Check first sheet
    first_sheet = sheets[0]['properties']['title']

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{first_sheet}'!A1:Z30"
    ).execute()

    rows = result.get('values', [])
    print(f"\n\nPayroll Sheet: {first_sheet} (gid={sheets[0]['properties']['sheetId']})")
    print("="*150)
    for i, row in enumerate(rows[:30]):
        print(f"Row {i:2d}: {row}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
