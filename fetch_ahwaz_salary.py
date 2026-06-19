#!/usr/bin/env python3
"""
Fetch Ahwaz's current gross salary from Agent April Payroll 2026 sheet
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load token
with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 80)
print('SEARCHING FOR AHWAZ IN AGENT APRIL PAYROLL 2026')
print('=' * 80)
print()

# Get all sheet tabs
sheet_metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
sheets = sheet_metadata.get('sheets', [])

print(f'Found {len(sheets)} entities\n')

found = False

for sheet in sheets:
    sheet_name = sheet['properties']['title']
    sheet_id = sheet['properties']['sheetId']

    # Read first 200 rows to search for Ahwaz
    range_name = f'{sheet_name}!A1:I200'

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=range_name
        ).execute()

        values = result.get('values', [])

        if values:
            for row_idx, row in enumerate(values):
                if len(row) > 1 and 'Ahwaz' in str(row[1]):  # Column B = Employee Name
                    print(f'FOUND IN ENTITY: {sheet_name}')
                    print(f'Row {row_idx + 1}')
                    print()
                    print('Data:')
                    print(f'  Employee ID: {row[0] if len(row) > 0 else "N/A"}')
                    print(f'  Employee Name: {row[1] if len(row) > 1 else "N/A"}')
                    print(f'  Job Title: {row[2] if len(row) > 2 else "N/A"}')
                    print(f'  Department: {row[3] if len(row) > 3 else "N/A"}')
                    print(f'  CNIC: {row[4] if len(row) > 4 else "N/A"}')
                    print(f'  Joining Date: {row[5] if len(row) > 5 else "N/A"}')
                    print(f'  Bank: {row[6] if len(row) > 6 else "N/A"}')
                    print(f'  Account: {row[7] if len(row) > 7 else "N/A"}')
                    print(f'  Gross Salary: {row[8] if len(row) > 8 else "N/A"}')
                    print()
                    found = True
    except Exception as e:
        print(f'Error reading {sheet_name}: {e}')

if not found:
    print('Ahwaz not found in the sheet')

print('=' * 80)
