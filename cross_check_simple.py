#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SIMPLE CROSS-CHECK: Current Payroll Entries
List all commute and buscaro entries for manual verification
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

print('=' * 120)
print('PAYROLL ENTRIES: COMMUTE ALLOWANCE (Column N) vs BusCARO (Column W)')
print('=' * 120)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT']

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
    commute_idx = col_map.get('Commute Allowance', -1)
    buscaro_idx = col_map.get('BusCaro', -1)

    print(f'\n{"=" * 120}')
    print(f'{entity.upper()}')
    print(f'{"=" * 120}')
    print()

    if commute_idx >= 0:
        print(f'COMMUTE ALLOWANCE (Column N) - Allowance for NIETE ICT coaches:')
        print('-' * 120)

        commute_entries = []
        for row_idx, row in enumerate(values[1:], 2):
            emp_name = row[name_idx] if name_idx < len(row) else ''
            commute_val = row[commute_idx] if commute_idx < len(row) else ''

            if commute_val and str(commute_val).strip() and str(commute_val) != '0':
                clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
                commute_entries.append((clean_name, commute_val))

        if commute_entries:
            for name, val in commute_entries:
                print(f'  {name:40} = {val}')
        else:
            print('  (None)')

        print(f'\nTotal: {len(commute_entries)} employees with commute allowance')
        print()

    if buscaro_idx >= 0:
        print(f'BusCARO (Column W) - Travel service deduction:')
        print('-' * 120)

        buscaro_entries = []
        for row_idx, row in enumerate(values[1:], 2):
            emp_name = row[name_idx] if name_idx < len(row) else ''
            buscaro_val = row[buscaro_idx] if buscaro_idx < len(row) else ''

            if buscaro_val and str(buscaro_val).strip() and str(buscaro_val) != '0':
                clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
                buscaro_entries.append((clean_name, buscaro_val))

        if buscaro_entries:
            for name, val in buscaro_entries:
                print(f'  {name:40} = {val}')
        else:
            print('  (None)')

        print(f'\nTotal: {len(buscaro_entries)} employees with BusCaro deduction')
        print()

print('=' * 120)
print()
print('⚠️  NEXT: User will verify these entries against the source sheets and identify misplaced entries')
print()
