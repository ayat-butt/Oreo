#!/usr/bin/env python3
"""
Clear Income Tax column (Column R) from all 5 entities in Agent April Payroll 2026
Set all values to 0
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load token
with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)

# Build Sheets API service
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

# Sheet ID for Agent April Payroll 2026
SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

# Entity ranges for Income Tax column (Column R = 18)
entities = [
    ('NIETE_Islamabad', 'R2:R85', 84),
    ('OPL', 'R2:R78', 77),
    ('OWT', 'R2:R22', 21),
    ('NIETE_Balochistan', 'R2:R2', 1),
    ('Taleemabad_Inc_', 'R2:R3', 2),
]

print('=' * 60)
print('CLEARING INCOME TAX COLUMN (COLUMN R)')
print('=' * 60)
print()

# Build batch update requests
requests = []
for entity_name, cell_range, count in entities:
    print(f'Preparing {entity_name}: {cell_range} ({count} rows)')
    values = [[0] for _ in range(count)]
    requests.append({
        'range': f'{entity_name}!{cell_range}',
        'values': values
    })

print()
print('Total requests:', len(requests))
print()

# Execute batch update
body = {
    'data': requests,
    'valueInputOption': 'RAW'
}

print('Executing batch update...')
result = service.spreadsheets().values().batchUpdate(
    spreadsheetId=SHEET_ID,
    body=body
).execute()

print()
print('=' * 60)
print('BATCH UPDATE COMPLETE')
print('=' * 60)
print()

total_cells = result.get('totalUpdatedCells', 0)
print(f'Total cells updated: {total_cells}')
print()

for i, (entity_name, _, count) in enumerate(entities):
    print(f'{entity_name}: {count} cells cleared to 0')

print()
print('SUCCESS: Income Tax column cleared from all 5 entities')
print()
