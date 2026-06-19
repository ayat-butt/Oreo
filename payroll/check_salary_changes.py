#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check salary changes across all months for Abdul Waheed and others
Show how salary changes affect tax calculation
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

# Payroll sheets from Jul 2025 to Apr 2026
sheets_to_check = [
    ('1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk', 'March 2026'),
    ('1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E', 'April 2026 (Revised)'),
]

print('=' * 120)
print('CHECKING SALARY CHANGES - Abdul Waheed')
print('=' * 120)
print()

for sheet_id, sheet_name in sheets_to_check:
    print(f'{sheet_name}:')
    print()

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f'NIETE_Islamabad!A1:R500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found\n')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    gross_idx = col_map.get('Gross Salary', -1)
    basic_idx = col_map.get('Basic Salary', -1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    for row in values[1:]:
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if 'Abdul Waheed' not in emp_name:
            continue

        gross = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
        basic = row[basic_idx] if basic_idx >= 0 and basic_idx < len(row) else ''
        taxable = row[taxable_idx] if taxable_idx >= 0 and taxable_idx < len(row) else ''
        income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''

        print(f'  Gross: {gross}')
        print(f'  Basic: {basic}')
        print(f'  Taxable: {taxable}')
        print(f'  Income Tax: {income_tax}')
        print()

print()
print('=' * 120)
print('CHECKING TAX DETAILS IN APRIL - Abdul Waheed')
print('=' * 120)
print()

REVISED_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'

result = service.spreadsheets().values().get(
    spreadsheetId=REVISED_SHEET_ID,
    range=f'NIETE_Islamabad!A1:AI500'
).execute()

values = result.get('values', [])
if values:
    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    gross_idx = col_map.get('Gross Salary', -1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)
    ytd_idx = col_map.get('YTD Taxable (Jul–Feb)', -1)
    annual_tax_idx = col_map.get('Annual Tax Liability (FBR)', -1)
    tax_collected_idx = col_map.get('Tax Collected So Far (Jul–Feb)', -1)

    for row in values[1:]:
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if 'Abdul Waheed' not in emp_name:
            continue

        gross = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
        taxable = row[taxable_idx] if taxable_idx >= 0 and taxable_idx < len(row) else ''
        income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''
        ytd = row[ytd_idx] if ytd_idx >= 0 and ytd_idx < len(row) else ''
        annual_tax = row[annual_tax_idx] if annual_tax_idx >= 0 and annual_tax_idx < len(row) else ''
        tax_collected = row[tax_collected_idx] if tax_collected_idx >= 0 and tax_collected_idx < len(row) else ''

        print('Abdul Waheed - April 2026 Tax Details:')
        print()
        print(f'  Gross Salary: {gross}')
        print(f'  Taxable Salary: {taxable}')
        print(f'  YTD Taxable (Jul-Feb): {ytd}')
        print(f'  Annual Tax Liability (FBR): {annual_tax}')
        print(f'  Tax Collected So Far (Jul-Feb): {tax_collected}')
        print(f'  April Income Tax: {income_tax}')
        print()

        # Calculate what April tax should be
        try:
            annual_tax_num = float(str(annual_tax).replace(',', '').strip()) if annual_tax else 0
            tax_collected_num = float(str(tax_collected).replace(',', '').strip()) if tax_collected else 0
            income_tax_num = float(str(income_tax).replace(',', '').strip()) if income_tax else 0

            remaining = annual_tax_num - tax_collected_num
            expected_monthly = remaining / 4 if remaining > 0 else 0

            print(f'CALCULATION:')
            print(f'  Remaining Tax = {annual_tax_num:,.0f} - {tax_collected_num:,.0f} = {remaining:,.0f}')
            print(f'  Expected Monthly (÷4) = {expected_monthly:,.0f}')
            print(f'  Actual April Tax = {income_tax_num:,.0f}')
            print(f'  Difference = {income_tax_num - expected_monthly:,.0f}')
            print()
            print(f'Question: Did salary change? That would explain the difference.')
            print()

        except:
            pass
