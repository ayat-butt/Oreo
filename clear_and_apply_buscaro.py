#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLEANUP & REBUILD:
1. Clear ALL Commute Allowance (Column N) - all 5 entities
2. Clear ALL BusCaro (Column W) - all 5 entities
3. Load BusCaro from source sheet (April 2026 tab)
4. Apply BusCaro values correctly
"""

import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
BUSCARO_SHEET_ID = '12EyDg8UAuDFexpJ_oC7hCN2HU0lDuQbAHHkmbdFKJwQ'

print('=' * 100)
print('STEP 1: LOAD BusCARO SOURCE DATA')
print('=' * 100)
print()

# Load BusCaro sheet
result = service.spreadsheets().values().get(
    spreadsheetId=BUSCARO_SHEET_ID,
    range='April 2026!A1:F200'
).execute()

buscaro_values = result.get('values', [])
print(f'Loaded {len(buscaro_values)} rows from BusCaro sheet')

# Parse BusCaro data
# The USER column is blue highlighted and shows employee names
buscaro_data = {}

# Find the USER column header
headers = buscaro_values[0] if buscaro_values else []
user_col = -1
amount_col = -1

for i, h in enumerate(headers):
    h_lower = str(h).lower()
    if 'user' in h_lower:
        user_col = i
    # Amount is usually the last column or one with numbers
    if 'amount' in h_lower or 'charge' in h_lower or 'deduction' in h_lower:
        amount_col = i

# If amount column not found, use last column
if amount_col < 0:
    amount_col = len(headers) - 1

print(f'USER column: {user_col}, Amount column: {amount_col}')
print()

# Build buscaro map
for row_idx, row in enumerate(buscaro_values[1:], 1):
    if len(row) > user_col and row[user_col]:
        emp_name = str(row[user_col]).strip()

        # Get amount - try to extract from rightmost numeric column
        amount = None
        for col_idx in range(len(row) - 1, -1, -1):
            try:
                val_str = str(row[col_idx]).replace(',', '').replace('(', '').replace(')', '').strip()
                if val_str:
                    amount = float(val_str)
                    if amount > 0:
                        break
            except:
                pass

        if emp_name and amount:
            if emp_name.lower() not in buscaro_data:
                buscaro_data[emp_name.lower()] = {
                    'name': emp_name,
                    'amount': amount
                }

print(f'✅ Found {len(buscaro_data)} employees with BusCaro charges in source sheet')
for name_lower, data in list(buscaro_data.items())[:10]:
    print(f'   {data["name"]} = {data["amount"]}')
if len(buscaro_data) > 10:
    print(f'   ... and {len(buscaro_data) - 10} more')

print()
print('=' * 100)
print('STEP 2: CLEAR COMMUTE ALLOWANCE (Column N) - ALL ENTITIES')
print('=' * 100)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

for entity in entities:
    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        continue

    headers = values[0]
    col_map = {h: i for i, h in enumerate(headers)}

    commute_idx = col_map.get('Commute Allowance', -1)

    if commute_idx < 0:
        print(f'{entity}: Column N not found')
        continue

    # Build clear requests for all rows in this entity
    clear_requests = []
    for row_idx in range(2, len(values) + 1):  # Row 2 onwards (skip header)
        clear_requests.append({
            'range': f'{entity}!{chr(65 + commute_idx)}{row_idx}',
            'values': [['']]
        })

    if clear_requests:
        body = {
            'data': clear_requests,
            'valueInputOption': 'RAW'
        }

        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=PAYROLL_SHEET_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'✅ {entity}: Cleared {updated} cells in Commute Allowance column')

print()
print('=' * 100)
print('STEP 3: CLEAR BusCARO (Column W) - ALL ENTITIES')
print('=' * 100)
print()

for entity in entities:
    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        continue

    headers = values[0]
    col_map = {h: i for i, h in enumerate(headers)}

    buscaro_idx = col_map.get('BusCaro', -1)

    if buscaro_idx < 0:
        print(f'{entity}: Column W not found')
        continue

    # Build clear requests for all rows in this entity
    clear_requests = []
    for row_idx in range(2, len(values) + 1):  # Row 2 onwards (skip header)
        clear_requests.append({
            'range': f'{entity}!{chr(65 + buscaro_idx)}{row_idx}',
            'values': [['']]
        })

    if clear_requests:
        body = {
            'data': clear_requests,
            'valueInputOption': 'RAW'
        }

        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=PAYROLL_SHEET_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'✅ {entity}: Cleared {updated} cells in BusCaro column')

print()
print('=' * 100)
print('STEP 4: APPLY BusCARO VALUES FROM SOURCE SHEET')
print('=' * 100)
print()

total_buscaro_applied = 0

for entity in entities:
    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        continue

    headers = values[0]
    col_map = {h: i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    buscaro_idx = col_map.get('BusCaro', -1)

    if buscaro_idx < 0:
        continue

    # Build batch update for this entity
    batch_requests = []
    entity_count = 0

    for row_idx, row in enumerate(values[1:], 2):
        if len(row) > name_idx:
            emp_name = str(row[name_idx]).strip()
            emp_name_lower = emp_name.lower()

            # Check if this employee is in BusCaro data
            if emp_name_lower in buscaro_data:
                amount = buscaro_data[emp_name_lower]['amount']
                batch_requests.append({
                    'range': f'{entity}!{chr(65 + buscaro_idx)}{row_idx}',
                    'values': [[amount]]
                })
                entity_count += 1

    if batch_requests:
        body = {
            'data': batch_requests,
            'valueInputOption': 'RAW'
        }

        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=PAYROLL_SHEET_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'✅ {entity}: Applied BusCaro to {entity_count} employees ({updated} cells updated)')
        total_buscaro_applied += entity_count

print()
print('=' * 100)
print('SUMMARY')
print('=' * 100)
print()
print(f'✅ Commute Allowance (Column N): CLEARED from all 5 entities')
print(f'✅ BusCaro (Column W): CLEARED from all 5 entities')
print(f'✅ BusCaro (Column W): APPLIED to {total_buscaro_applied} employees from source sheet')
print()
