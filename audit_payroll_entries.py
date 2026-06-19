#!/usr/bin/env python
"""
SIMPLE PAYROLL AUDIT - Read current payroll and identify suspicious entries
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 100)
print('PAYROLL AUDIT - April 2026')
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

    # Build column index map
    col_map = {}
    for i, h in enumerate(headers):
        col_map[h] = i

    # Key columns we're checking
    name_idx = col_map.get('Employee Name', 1)
    id_idx = col_map.get('Employee ID', 0)
    commute_idx = col_map.get('Commute Allowance', -1)
    overtime_idx = col_map.get('Overtime', -1)
    advance_idx = col_map.get('Advance', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    print(f'\n{entity.upper()}')
    print('-' * 100)

    # Check for employees with non-zero Commute values
    if commute_idx >= 0:
        print(f'\nEmployees with Commute Allowance (Column N):')
        commute_count = 0
        for row_idx, row in enumerate(values[1:], 2):
            if len(row) > commute_idx:
                emp_name = row[name_idx] if name_idx < len(row) else ''
                emp_id = row[id_idx] if id_idx < len(row) else ''
                commute_val = row[commute_idx] if commute_idx < len(row) else ''

                if commute_val and str(commute_val).strip() and str(commute_val) != '0':
                    print(f"  Row {row_idx}: ID {emp_id} | {emp_name} = {commute_val}")
                    commute_count += 1

        print(f'  Total: {commute_count} employees with commute allowance')

    # Check for missing Income Tax
    if income_tax_idx >= 0:
        print(f'\nEmployees with MISSING Income Tax (Column R):')
        missing_tax = 0
        for row_idx, row in enumerate(values[1:], 2):
            if len(row) > income_tax_idx:
                emp_name = row[name_idx] if name_idx < len(row) else ''
                emp_id = row[id_idx] if id_idx < len(row) else ''
                tax_val = row[income_tax_idx] if income_tax_idx < len(row) else ''

                if not tax_val or str(tax_val).strip() == '' or str(tax_val).strip() == '0':
                    # Check if this is a new joiner (should we check unpaid days?)
                    print(f"  Row {row_idx}: ID {emp_id} | {emp_name}")
                    missing_tax += 1

        if missing_tax > 0:
            print(f'  Total: {missing_tax} employees missing income tax')

print('\n' + '=' * 100)
