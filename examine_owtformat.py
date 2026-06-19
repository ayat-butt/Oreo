#!/usr/bin/env python3
"""Examine the OWT sample format to understand output structure"""

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

# Sample OWT format sheet
spreadsheet_id = '1I1cd_67TyDjU7ACFOi7T7X_EzH88fNs8i_VeWVJUc5U'

try:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get('sheets', [])

    print("Sheets in OWT sample format:")
    for sheet in sheets:
        print(f"  - {sheet['properties']['title']}")

    # Get the first sheet data
    first_sheet = sheets[0]['properties']['title']

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{first_sheet}'!A1:Z50"
    ).execute()

    rows = result.get('values', [])
    print(f"\n\nOWT Format Sheet: {first_sheet}")
    print("="*120)
    for i, row in enumerate(rows[:50]):
        print(f"Row {i:2d}: {row}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
