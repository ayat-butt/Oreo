#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recalculate April 2026 income tax using Pakistan FBR progressive tax slabs
Compare with actual values to identify exact error
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
print('RECALCULATING TAX WITH PAKISTAN FBR PROGRESSIVE TAX SLABS')
print('=' * 120)
print()

# Pakistan FBR Tax Slabs for 2025-2026
# (Income bracket lower limit, income bracket upper limit, rate)
TAX_SLABS = [
    (0, 600000, 0.00),
    (600000, 1000000, 0.05),
    (1000000, 1500000, 0.10),
    (1500000, 2500000, 0.15),
    (2500000, 3500000, 0.20),
    (3500000, 4000000, 0.25),
    (4000000, 5000000, 0.30),
    (5000000, float('inf'), 0.35)
]

def calculate_tax_with_slabs(taxable_salary):
    """Calculate tax using progressive tax slabs"""
    if taxable_salary <= 0:
        return 0

    tax = 0
    for lower, upper, rate in TAX_SLABS:
        if taxable_salary <= lower:
            break

        # Income in this bracket
        taxable_in_bracket = min(taxable_salary, upper) - lower
        tax += taxable_in_bracket * rate

    return tax

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('Tax Slabs Used:')
for lower, upper, rate in TAX_SLABS:
    if upper == float('inf'):
        print(f'  {lower:>10,.0f} and above: {rate*100:>5.1f}%')
    else:
        print(f'  {lower:>10,.0f} - {upper:>10,.0f}: {rate*100:>5.1f}%')

print()
print('=' * 120)
print('COMPARISON: CALCULATED VS ACTUAL TAX')
print('=' * 120)
print()

all_comparisons = []
total_error = 0
total_employees = 0

for entity in entities:
    print(f'{entity}:')
    print()

    result = service.spreadsheets().values().get(
        spreadsheetId=REVISED_SHEET_ID,
        range=f'{entity}!A1:R500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found\n')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    gross_idx = col_map.get('Gross Salary', -1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    if income_tax_idx < 0:
        print('  Income Tax column not found\n')
        continue

    entity_comparisons = []

    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        gross_sal = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
        taxable_sal = row[taxable_idx] if taxable_idx >= 0 and taxable_idx < len(row) else ''
        actual_tax = row[income_tax_idx] if income_tax_idx < len(row) else ''

        if not emp_name:
            continue

        try:
            actual_tax_num = float(str(actual_tax).replace(',', '').strip()) if actual_tax else 0

            # Use Taxable Salary if available, otherwise use Gross Salary
            if taxable_sal and str(taxable_sal).strip():
                calc_base = float(str(taxable_sal).replace(',', '').strip())
            else:
                calc_base = float(str(gross_sal).replace(',', '').strip()) if gross_sal else 0

            calculated_tax = calculate_tax_with_slabs(calc_base)
            error = actual_tax_num - calculated_tax
            error_percent = (error / actual_tax_num * 100) if actual_tax_num > 0 else 0

            entity_comparisons.append({
                'name': emp_name,
                'actual': actual_tax_num,
                'calculated': calculated_tax,
                'error': error,
                'error_percent': error_percent
            })

            total_error += abs(error)
            total_employees += 1

        except:
            pass

    # Show first 10 comparisons for this entity
    if entity_comparisons:
        print(f'Employee Name{" "*25} | Calculated | Actual      | Difference | Error %')
        print('-' * 120)

        for comp in entity_comparisons[:10]:
            clean_name = comp['name'].encode('utf-8', errors='ignore').decode('utf-8')
            print(f'{clean_name:<30} | {comp["calculated"]:>11,.0f} | {comp["actual"]:>11,.0f} | {comp["error"]:>10,.0f} | {comp["error_percent"]:>6.2f}%')

        all_comparisons.extend(entity_comparisons)
        print()

print()
print('=' * 120)
print('SUMMARY - ERROR ANALYSIS')
print('=' * 120)
print()

if all_comparisons:
    total_actual = sum(c['actual'] for c in all_comparisons)
    total_calculated = sum(c['calculated'] for c in all_comparisons)

    print(f'Total Employees Analyzed: {len(all_comparisons)}')
    print(f'Total Actual Tax: {total_actual:,.0f} PKR')
    print(f'Total Calculated Tax: {total_calculated:,.0f} PKR')
    print(f'Total Difference: {total_actual - total_calculated:,.0f} PKR')
    print(f'Average Error per Employee: {total_error / len(all_comparisons):,.0f} PKR')
    print()

    # Find largest errors
    sorted_by_error = sorted(all_comparisons, key=lambda x: abs(x['error']), reverse=True)

    print('Top 10 Largest Discrepancies:')
    print()
    for idx, comp in enumerate(sorted_by_error[:10], 1):
        clean_name = comp['name'].encode('utf-8', errors='ignore').decode('utf-8')
        print(f'{idx}. {clean_name}')
        print(f'   Calculated: {comp["calculated"]:,.0f} | Actual: {comp["actual"]:,.0f} | Difference: {comp["error"]:,.0f} ({comp["error_percent"]:.2f}%)')
        print()
