#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final verification: April 2026 income tax application
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

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 120)
print('FINAL VERIFICATION: APRIL 2026 INCOME TAX')
print('=' * 120)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('INCOME TAX STATUS BY ENTITY')
print('-' * 120)
print()

total_with_tax = 0
total_zero_tax = 0
total_missing_tax = 0
new_joiners = []

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
    income_tax_idx = col_map.get('Income Tax', -1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    joining_idx = col_map.get('Joining Date', -1)

    with_tax = 0
    zero_tax = 0
    missing_tax = 0

    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        tax_val = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''
        taxable_sal = row[taxable_idx] if taxable_idx >= 0 and taxable_idx < len(row) else ''
        joining_date = row[joining_idx] if joining_idx >= 0 and joining_idx < len(row) else ''

        if not emp_name:
            continue

        if not tax_val or str(tax_val).strip() == '':
            missing_tax += 1
            clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
            new_joiners.append({
                'entity': entity,
                'name': clean_name,
                'taxable_salary': taxable_sal,
                'joining_date': joining_date
            })
        elif str(tax_val).strip() == '0':
            zero_tax += 1
        else:
            try:
                tax_num = float(str(tax_val).replace(',', '').strip())
                if tax_num > 0:
                    with_tax += 1
                else:
                    zero_tax += 1
            except:
                zero_tax += 1

    total_with_tax += with_tax
    total_zero_tax += zero_tax
    total_missing_tax += missing_tax

    print(f'{entity:25} | With tax: {with_tax:3} | Zero tax: {zero_tax:3} | Missing: {missing_tax:2}')

print()
print('=' * 120)
print('TOTAL SUMMARY')
print('=' * 120)
print()
print(f'Employees with income tax: {total_with_tax:3}')
print(f'Employees with zero tax:   {total_zero_tax:3}')
print(f'Employees missing tax:     {total_missing_tax:2}')
print(f'TOTAL:                     {total_with_tax + total_zero_tax + total_missing_tax:3}/185')
print()

if new_joiners:
    print('=' * 120)
    print('NEW JOINERS - NEED MANUAL TAX CALCULATION')
    print('=' * 120)
    print()

    for joiner in new_joiners:
        clean_name = joiner['name']
        taxable_sal = joiner['taxable_salary']

        print(f'{joiner["entity"]:25} | {clean_name:30} | Taxable: {taxable_sal}')
        print()

    print('These new joiners should have April income tax calculated based on:')
    print('  - Their Taxable Salary (April only, no 9-month history)')
    print('  - Pakistan tax slabs for April 2026')
    print('  - No financial year deduction needed (they just joined)')
    print()

print('=' * 120)
print('[COMPLETE] April 2026 Income Tax Application')
print('=' * 120)
print()
