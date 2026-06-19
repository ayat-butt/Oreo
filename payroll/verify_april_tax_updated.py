#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify that April Income Tax has been properly calculated and updated
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

AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 120)
print('VERIFYING APRIL INCOME TAX CALCULATIONS IN AGENT PAYROLL')
print('=' * 120)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

for entity in entities:
    print(f'{entity}:')
    print()

    result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:AI500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found\n')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    annual_tax_idx = col_map.get('Annual Tax Liability (FBR)', -1)
    tax_collected_idx = col_map.get('Tax Collected So Far (Jul–Feb)', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    if income_tax_idx < 0:
        print('  Income Tax column not found\n')
        continue

    print(f'Employee Name{" "*25} | Annual Tax | Collected | Expected Apr | Actual Apr | Match')
    print('-' * 120)

    sample_count = 0
    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if not emp_name:
            continue

        annual_tax = row[annual_tax_idx] if annual_tax_idx >= 0 and annual_tax_idx < len(row) else ''
        tax_collected = row[tax_collected_idx] if tax_collected_idx >= 0 and tax_collected_idx < len(row) else ''
        income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''

        try:
            annual_tax_num = float(str(annual_tax).replace(',', '').strip()) if annual_tax else 0
            tax_collected_num = float(str(tax_collected).replace(',', '').strip()) if tax_collected else 0
            income_tax_num = float(str(income_tax).replace(',', '').strip()) if income_tax else 0

            expected_apr = (annual_tax_num - tax_collected_num) / 4

            # Check if it matches
            match = "✓" if abs(income_tax_num - expected_apr) < 1 else "✗"

            if sample_count < 5:
                clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
                print(f'{clean_name:<30} | {annual_tax_num:>10,.0f} | {tax_collected_num:>9,.0f} | {expected_apr:>12,.0f} | {income_tax_num:>10,.0f} | {match}')
                sample_count += 1

        except:
            pass

    print()

print()
print('=' * 120)
print('LEGEND')
print('=' * 120)
print()
print('✓ = Income Tax matches expected calculation: (Annual Tax - Collected) ÷ 4')
print('✗ = Mismatch - may need review')
print()
