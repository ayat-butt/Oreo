#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse BusCaro sheet correctly with proper understanding of structure
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
print('PARSING BusCARO - April 2026')
print('=' * 100)
print()

# Load all columns from BusCaro
result = service.spreadsheets().values().get(
    spreadsheetId=BUSCARO_SHEET_ID,
    range='April 2026!A1:Z200'
).execute()

buscaro_values = result.get('values', [])

print(f'Loaded {len(buscaro_values)} rows')
print()

# The sheet structure seems to be:
# Row 3: Route header with amount (42 in column G?)
# Row 4: Column headers (Name, Station, etc)
# Rows 5+: Employee data
# Column B appears to have employee names

# Let's look for where the amount might be
print('Looking for amount columns...')
print()

# Show more rows to understand structure
print('First 20 rows (all columns):')
for i, row in enumerate(buscaro_values[:20], 1):
    print(f'Row {i}: {row}')

print()

# Build BusCaro map based on Column B (employee names)
buscaro_data = {}

for row_idx, row in enumerate(buscaro_values[4:], 5):  # Start from row 5 (after headers)
    if len(row) > 1 and row[1]:  # Column B has employee name
        emp_name = str(row[1]).strip()

        if emp_name and emp_name.lower() not in ['name', '']:
            # Amount might be in column G (index 6) based on the pattern
            amount = None

            # Try to find amount from columns G onwards
            for col_idx in range(6, len(row)):
                try:
                    val_str = str(row[col_idx]).replace(',', '').replace('(', '').replace(')', '').strip()
                    if val_str and val_str not in ['', '0', 'true', 'false']:
                        try:
                            val_num = float(val_str)
                            if val_num > 0 and val_num < 50000:  # Reasonable amount
                                amount = val_num
                                break
                        except:
                            pass
                except:
                    pass

            if emp_name:
                if emp_name.lower() not in buscaro_data:
                    buscaro_data[emp_name.lower()] = {
                        'name': emp_name,
                        'amount': amount
                    }

print(f'✅ Found {len(buscaro_data)} employees in BusCaro sheet')
print()
print('Employees with charges:')
for name_lower, data in sorted(buscaro_data.items()):
    if data['amount']:
        print(f'  {data["name"]} = {data["amount"]}')

print()
print('=' * 100)
print('APPLYING TO PAYROLL')
print('=' * 100)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

# First CLEAR all BusCaro
print('Step 1: CLEARING all BusCaro columns...')
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

    if buscaro_idx >= 0:
        clear_requests = []
        for row_idx in range(2, min(len(values) + 1, 300)):
            clear_requests.append({
                'range': f'{entity}!{chr(65 + buscaro_idx)}{row_idx}',
                'values': [['']]
            })

        if clear_requests:
            body = {'data': clear_requests, 'valueInputOption': 'RAW'}
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=PAYROLL_SHEET_ID,
                body=body
            ).execute()
            print(f'  ✅ {entity}: Cleared BusCaro column')

# Then CLEAR all Commute
print()
print('Step 2: CLEARING all Commute Allowance columns...')
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

    if commute_idx >= 0:
        clear_requests = []
        for row_idx in range(2, min(len(values) + 1, 300)):
            clear_requests.append({
                'range': f'{entity}!{chr(65 + commute_idx)}{row_idx}',
                'values': [['']]
            })

        if clear_requests:
            body = {'data': clear_requests, 'valueInputOption': 'RAW'}
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=PAYROLL_SHEET_ID,
                body=body
            ).execute()
            print(f'  ✅ {entity}: Cleared Commute Allowance column')

# Apply BusCaro
print()
print('Step 3: APPLYING BusCaro from source...')
total_applied = 0

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

    batch_requests = []
    entity_count = 0

    for row_idx, row in enumerate(values[1:], 2):
        if len(row) > name_idx:
            emp_name = str(row[name_idx]).strip()
            emp_name_lower = emp_name.lower()

            if emp_name_lower in buscaro_data and buscaro_data[emp_name_lower]['amount']:
                amount = buscaro_data[emp_name_lower]['amount']
                batch_requests.append({
                    'range': f'{entity}!{chr(65 + buscaro_idx)}{row_idx}',
                    'values': [[amount]]
                })
                entity_count += 1

    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=PAYROLL_SHEET_ID,
            body=body
        ).execute()
        print(f'  ✅ {entity}: Applied to {entity_count} employees')
        total_applied += entity_count

print()
print(f'✅ TOTAL BusCaro applied: {total_applied} employees')
print()
