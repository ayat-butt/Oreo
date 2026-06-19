#!/usr/bin/env python3
"""Find date columns in addition/deletion sheets"""

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

# Check one of the payroll sheets with addition/deletion
sheets_to_check = [
    ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL', 'November 2024'),
    ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL', 'December 2024'),
]

for sheet_id, tab, month in sheets_to_check:
    print(f"\n{'='*150}")
    print(f"Checking {month} - Tab: {tab}")
    print(f"{'='*150}\n")

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab}'!A1:Z100"
        ).execute()

        rows = result.get('values', [])

        for i, row in enumerate(rows[:50]):
            print(f"Row {i:2d}: {row}")

    except Exception as e:
        print(f"Error: {e}")
