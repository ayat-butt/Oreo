#!/usr/bin/env python3
"""Check for entity column in payroll"""

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
    # Get all columns
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="'July, 2024'!A1:AA100"
    ).execute()

    rows = result.get('values', [])
    print("July 2024 - Full row view (first 50 rows, all columns)")
    print("="*200)

    # Print header rows
    for i in range(0, 3):
        row = rows[i] if i < len(rows) else []
        col_letters = [chr(65 + j) if j < 26 else f"A{chr(65 + j - 26)}" for j in range(len(row))]
        print(f"\nRow {i}:")
        for col, val in enumerate(row):
            if col < 20:  # Print first 20 columns
                print(f"  {col_letters[col] if col < len(col_letters) else 'Z'}: {val}")
        if len(row) > 20:
            print(f"  ... ({len(row)} total columns)")

    # Show some data rows
    print("\n\nData rows 5-15:")
    for i in range(5, min(15, len(rows))):
        row = rows[i]
        print(f"Row {i}: {row[:20]}")  # Show first 20 columns

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
