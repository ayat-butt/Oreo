#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check the structure of the new payroll sheet
See what columns exist and what calculations are needed
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

NEW_SHEET_ID = '14Ht2gr3YCwaDzJVDvHzEIYhMY-Q89QpgkNvzwKSAkLA'

print('=' * 160)
print('EXPLORING NEW PAYROLL SHEET STRUCTURE')
print('=' * 160)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

for entity in entities:
    print(f'{entity}:')
    print()

    result = service.spreadsheets().values().get(
        spreadsheetId=NEW_SHEET_ID,
        range=f'{entity}!A1:AJ1'
    ).execute()

    values = result.get('values', [])
    if values:
        headers = values[0]
        print('Available columns:')
        for idx, h in enumerate(headers):
            col_letter = chr(65 + idx) if idx < 26 else chr(64 + idx // 26) + chr(65 + idx % 26)
            print(f'  {col_letter:3s} ({idx:2d}): {h}')
    else:
        print('  No headers found')

    print()

print()
print('=' * 160)
print('SAMPLE DATA')
print('=' * 160)
print()

for entity in entities:
    print(f'{entity}:')
    print()

    result = service.spreadsheets().values().get(
        spreadsheetId=NEW_SHEET_ID,
        range=f'{entity}!A1:AA10'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found\n')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    total_allow_idx = col_map.get('Total Allowance', -1)
    medical_idx = col_map.get('Medical Allowance', -1)
    unpaid_idx = col_map.get('Unpaid Days', -1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    print('First 3 employees:')
    sample_count = 0
    for row in values[1:]:
        if sample_count >= 3:
            break

        emp_name = row[name_idx] if name_idx < len(row) else ''
        if not emp_name:
            continue

        total_allow = row[total_allow_idx] if total_allow_idx >= 0 and total_allow_idx < len(row) else ''
        medical = row[medical_idx] if medical_idx >= 0 and medical_idx < len(row) else ''
        unpaid = row[unpaid_idx] if unpaid_idx >= 0 and unpaid_idx < len(row) else ''
        taxable = row[taxable_idx] if taxable_idx >= 0 and taxable_idx < len(row) else ''
        income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''

        clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
        print(f'  {clean_name}')
        print(f'    Total Allowance: {total_allow}')
        print(f'    Medical Allow: {medical}')
        print(f'    Unpaid Days: {unpaid}')
        print(f'    Taxable Salary: {taxable}')
        print(f'    Income Tax: {income_tax}')
        print()

        sample_count += 1

    print()
