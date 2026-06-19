#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze actual April 2026 income tax values from Revised sheet
Try to identify the methodology/pattern used
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

REVISED_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'

print('=' * 120)
print('ANALYZING ACTUAL APRIL 2026 INCOME TAX - REVISED SHEET')
print('=' * 120)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

all_comparisons = []

for entity in entities:
    print(f'{entity}:')
    print()

    result = service.spreadsheets().values().get(
        spreadsheetId=REVISED_SHEET_ID,
        range=f'{entity}!A1:R500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    gross_idx = col_map.get('Gross Salary', -1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    if income_tax_idx < 0:
        print('  Income Tax column not found')
        continue

    # Show first 10 employees with their details
    sample_count = 0
    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        gross_sal = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
        taxable_sal = row[taxable_idx] if taxable_idx >= 0 and taxable_idx < len(row) else ''
        income_tax = row[income_tax_idx] if income_tax_idx < len(row) else ''

        if not emp_name or not income_tax:
            continue

        # Try to calculate tax rate
        try:
            tax_num = float(str(income_tax).replace(',', '').strip()) if income_tax else 0
            taxable_num = float(str(taxable_sal).replace(',', '').strip()) if taxable_sal else 0
            gross_num = float(str(gross_sal).replace(',', '').strip()) if gross_sal else 0

            if taxable_num > 0:
                tax_rate = (tax_num / taxable_num) * 100
            else:
                tax_rate = 0

            if sample_count < 10:
                clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
                print(f'{sample_count+1}. {clean_name}')
                print(f'   Gross: {gross_sal} | Taxable: {taxable_sal} | Tax: {income_tax}')
                print(f'   Tax Rate: {tax_rate:.2f}% of Taxable Salary')
                print()
                sample_count += 1

                all_comparisons.append({
                    'entity': entity,
                    'name': emp_name,
                    'gross': gross_num,
                    'taxable': taxable_num,
                    'tax': tax_num,
                    'tax_rate': tax_rate
                })

        except:
            pass

print()
print('=' * 120)
print('ANALYSIS - TAX RATE PATTERN')
print('=' * 120)
print()

if all_comparisons:
    # Calculate average tax rate
    avg_tax_rate = sum(c['tax_rate'] for c in all_comparisons) / len(all_comparisons) if all_comparisons else 0
    min_rate = min(all_comparisons, key=lambda x: x['tax_rate']) if all_comparisons else None
    max_rate = max(all_comparisons, key=lambda x: x['tax_rate']) if all_comparisons else None

    print(f'Average Tax Rate: {avg_tax_rate:.2f}%')
    print(f'Min Tax Rate: {min_rate["tax_rate"]:.2f}% ({min_rate["name"]})')
    print(f'Max Tax Rate: {max_rate["tax_rate"]:.2f}% ({max_rate["name"]})')
    print()

    # Group by tax rate ranges
    print('Distribution by Tax Rate:')
    ranges = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30), (30, 35)]
    for min_r, max_r in ranges:
        count = sum(1 for c in all_comparisons if min_r <= c['tax_rate'] < max_r)
        if count > 0:
            print(f'  {min_r}% - {max_r}%: {count} employees')
