#!/usr/bin/env python3
"""Check July 2024 payroll sheet"""

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

spreadsheet_id = '1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k'

try:
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="'July, 2024'!A1:M50"
    ).execute()

    rows = result.get('values', [])
    print("July 2024 Payroll Sheet")
    print("="*180)
    for i, row in enumerate(rows[:50]):
        if i < 10 or i > 40:
            print(f"Row {i:2d}: {row}")
        elif i == 10:
            print("...")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
