#!/usr/bin/env python3
"""Debug script to see actual data in sheets"""

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
spreadsheet_id = '1-GEd1hIU7OOJ-CP97VqnrW1p0TPTXhzDAlgim08HLJM'

# Check May 2025 sheet (which we know has the structure)
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range="'May 2025'!A1:H50"
).execute()

rows = result.get('values', [])
print("May 2025 Sheet Data:")
print("="*100)
for i, row in enumerate(rows):
    print(f"Row {i:2d}: {row}")
