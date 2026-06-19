#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Apply calculated April 2026 income tax to payroll sheet
"""

import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('../token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

print('=' * 120)
print('APPLYING APRIL 2026 CALCULATED INCOME TAX TO PAYROLL')
print('=' * 120)
print()

# Load calculated April tax
with open('april_2026_tax_calculated.json', 'r') as f:
    april_tax_data = json.load(f)

print(f'Loaded calculated April tax for {len(april_tax_data)} employees')
print()

# Current April 2026 payroll
PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('APPLYING TAX TO APRIL 2026 PAYROLL')
print('-' * 120)
print()

total_applied = 0
total_not_found = 0
not_found_list = []

for entity in entities:
    print(f'{entity}:')

    # Load payroll
    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found')
        continue

    headers = values[0]
    col_map = {h: i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    income_tax_idx = col_map.get('Income Tax', -1)

    if income_tax_idx < 0:
        print('  Income Tax column not found')
        continue

    # Build batch update
    batch_requests = []
    entity_applied = 0

    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        emp_name_lower = emp_name.lower()

        # Check if this employee is in calculated tax data
        if emp_name_lower in april_tax_data:
            april_tax = april_tax_data[emp_name_lower].get('april_tax', 0)

            batch_requests.append({
                'range': f'{entity}!{chr(65 + income_tax_idx)}{row_idx}',
                'values': [[april_tax]]
            })
            entity_applied += 1
        else:
            # Not found in calculated data
            total_not_found += 1
            if total_not_found <= 10:
                clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
                not_found_list.append((entity, clean_name))

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=PAYROLL_SHEET_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  Applied: {entity_applied} employees')
        total_applied += entity_applied

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print(f'Total Income Tax applied: {total_applied}/185 employees')
print(f'Not found in calculated data: {total_not_found}')
print()

if not_found_list:
    print('Employees not found in calculated data (first 10):')
    for entity, name in not_found_list:
        print(f'  {entity:25} | {name}')
    print()

print('[SUCCESS] April 2026 income tax applied to payroll')
print()
