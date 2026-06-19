#!/usr/bin/env python
"""Find Tayyaba Hamna and check what commute allowance value was added"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

# Check all entities for Tayyaba Hamna
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('=' * 80)
print('SEARCHING FOR TAYYABA HAMNA')
print('=' * 80)
print()

for entity in entities:
    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    headers = values[0] if values else []

    # Find commute allowance column index
    commute_idx = -1
    buscaro_idx = -1
    for i, h in enumerate(headers):
        if 'commute' in str(h).lower():
            commute_idx = i
        if 'buscaro' in str(h).lower():
            buscaro_idx = i

    # Search for Tayyaba
    for row_idx, row in enumerate(values[1:], 1):
        if len(row) > 1 and 'tayyaba' in str(row[1]).lower():
            emp_id = row[0] if len(row) > 0 else ''
            emp_name = row[1] if len(row) > 1 else ''
            commute_val = row[commute_idx] if commute_idx >= 0 and commute_idx < len(row) else ''
            buscaro_val = row[buscaro_idx] if buscaro_idx >= 0 and buscaro_idx < len(row) else ''

            print(f"Found in {entity} (row {row_idx + 1}):")
            print(f"  Employee ID: {emp_id}")
            print(f"  Name: {emp_name}")
            print(f"  Commute Allowance (Col {chr(65 + commute_idx)}): {commute_val}")
            print(f"  BusCaro (Col {chr(65 + buscaro_idx)}): {buscaro_val}")
            print()

print('=' * 80)
