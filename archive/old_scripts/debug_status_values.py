#!/usr/bin/env python3
"""Debug status values in the sheet."""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
RANGE = "A1:I20"

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

service = build('sheets', 'v4', credentials=creds)
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=RANGE
).execute()

values = result.get('values', [])

print("Headers:")
for idx, h in enumerate(values[0]):
    print(f"  {idx}: {h}")

print("\nSample data:")
for row_idx, row in enumerate(values[1:6], start=2):
    print(f"\nRow {row_idx}:")
    for col_idx, val in enumerate(row):
        print(f"  Col {col_idx}: {val[:50] if len(val) > 50 else val}")
