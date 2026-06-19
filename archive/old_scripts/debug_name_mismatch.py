#!/usr/bin/env python3
"""
Debug name mismatches between CSV and Google Sheet.
"""

import csv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
RANGE = "A1:B100"

# Load from CSV
csv_names = set()
with open('output/GoogleCoordinates_ForSheet.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_names.add(row['Name'].strip())

print(f"[CSV] Loaded {len(csv_names)} names")

# Load from Sheet
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

if creds:
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])
    sheet_names = set()

    for row in values[1:]:
        if row:
            name = row[0].strip()
            sheet_names.add(name)

    print(f"[SHEET] Loaded {len(sheet_names)} names")

    # Find mismatches
    in_csv_not_sheet = csv_names - sheet_names
    in_sheet_not_csv = sheet_names - csv_names

    print(f"\n[MISMATCHES]")
    if in_csv_not_sheet:
        print(f"\nIn CSV but NOT in Sheet ({len(in_csv_not_sheet)}):")
        for name in sorted(in_csv_not_sheet)[:10]:
            print(f"  - {name}")

    if in_sheet_not_csv:
        print(f"\nIn Sheet but NOT in CSV ({len(in_sheet_not_csv)}):")
        for name in sorted(in_sheet_not_csv)[:10]:
            print(f"  - {name}")

    # Find potential matches
    print(f"\n[CHECKING] Potential partial matches...")
    matched = csv_names & sheet_names
    print(f"Exact matches: {len(matched)}/67")
