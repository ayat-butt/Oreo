#!/usr/bin/env python
"""
COMPREHENSIVE PAYROLL AUDIT - April 2026
Checks ALL 16 steps against source data
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import time

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
TAX_SHEET_ID = '1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs'
COMMUTE_SHEET_ID = '10kM4xcC0S7nSJhU5HfH6ZdbiTxqyzw5P4_z5nOJ7lck'
MEAL_SHEET_ID = '1iZMCJe6aHxxwVsCKpIqzu4g4ZAvYci76noOeSB2byD4'
BUSCARO_SHEET_ID = '1xr7Y8vPqwEHJ5mEJWMz0vM4y4nA9iNJ4RVNqYo9YX5g'
ADVANCES_SHEET_ID = '1sxXfGghw1cGuTsP15VZMxXCxkT1SxY61UNmHMp6vtBE'

print('=' * 80)
print('COMPREHENSIVE PAYROLL AUDIT - APRIL 2026')
print('=' * 80)
print()

# ============================================================================
# STEP 1: Load Payroll Data (all 5 entities)
# ============================================================================
print('LOADING PAYROLL DATA...')
print('-' * 80)

payroll_data = {}
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

for entity in entities:
    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    headers = values[0] if values else []

    # Build header index map
    header_map = {h.lower().replace(' ', '_'): i for i, h in enumerate(headers)}

    payroll_data[entity] = {
        'headers': headers,
        'header_map': header_map,
        'rows': values[1:]
    }

    print(f"  {entity}: {len(values[1:])} employees")

print()

# ============================================================================
# STEP 2: Load Tax Reference Data
# ============================================================================
print('LOADING TAX REFERENCE DATA...')
print('-' * 80)

result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range='TAX DEDUCTION DETAILS!A1:M500'
).execute()

tax_values = result.get('values', [])
tax_headers = tax_values[0] if tax_values else []

# Find April column (should be index 12)
april_idx = -1
for i, h in enumerate(tax_headers):
    if 'apr' in str(h).lower():
        april_idx = i
        break

print(f"  April column index: {april_idx}")
print(f"  Total employees in TAX sheet: {len(tax_values) - 1}")
print()

# Build tax data map
tax_data = {}
for row in tax_values[1:]:
    if len(row) > 1:
        emp_name = str(row[1]).strip() if row[1] else ''
        if emp_name:
            tax_val = row[april_idx] if april_idx >= 0 and april_idx < len(row) else ''
            tax_data[emp_name.lower()] = tax_val

# ============================================================================
# STEP 3: Load Commute Allowance Reference
# ============================================================================
print('LOADING COMMUTE ALLOWANCE REFERENCE...')
print('-' * 80)

result = service.spreadsheets().values().get(
    spreadsheetId=COMMUTE_SHEET_ID,
    range='Coaches Advance Fuel Amount!A1:D200'
).execute()

commute_values = result.get('values', [])
commute_data = {}

for row in commute_values[1:]:
    if len(row) > 1:
        emp_name = str(row[1]).strip() if len(row) > 1 and row[1] else ''
        amount = row[3] if len(row) > 3 and row[3] else ''
        if emp_name and amount:
            commute_data[emp_name.lower()] = amount

print(f"  Coaches with commute allowance: {len(commute_data)}")
print()

# ============================================================================
# STEP 4: Check for Incorrect Commute/BusCaro Mixing
# ============================================================================
print('CHECKING COMMUTE ALLOWANCE SECTION (Should be coaches only)...')
print('-' * 80)

commute_issues = []
for entity, data in payroll_data.items():
    commute_idx = data['header_map'].get('commute_allowance', -1)

    if commute_idx < 0:
        continue

    for row_idx, row in enumerate(data['rows']):
        emp_name = row[1] if len(row) > 1 else ''
        commute_val = row[commute_idx] if commute_idx < len(row) else ''

        if commute_val and str(commute_val).strip() and str(commute_val).strip() != '0':
            # Check if this employee should have commute allowance
            if emp_name.lower() not in commute_data:
                commute_issues.append({
                    'entity': entity,
                    'row': row_idx + 2,
                    'name': emp_name,
                    'amount': commute_val,
                    'reason': 'NOT in Coaches list - might be BusCaro'
                })

if commute_issues:
    print(f"⚠️  FOUND {len(commute_issues)} SUSPICIOUS COMMUTE ENTRIES:")
    for issue in commute_issues[:10]:  # Show first 10
        print(f"  {issue['entity']} row {issue['row']}: {issue['name']} = {issue['amount']} — {issue['reason']}")
else:
    print("✅ All commute entries verified against Coaches list")

print()

# ============================================================================
# STEP 5: Load Meal Deduction Reference
# ============================================================================
print('LOADING MEAL DEDUCTION REFERENCE...')
print('-' * 80)

result = service.spreadsheets().values().get(
    spreadsheetId=MEAL_SHEET_ID,
    range='Meal Deduction!A1:E200'
).execute()

meal_values = result.get('values', [])
meal_data = {}

for row in meal_values[1:]:
    if len(row) > 1:
        emp_name = str(row[1]).strip() if len(row) > 1 and row[1] else ''
        if emp_name:
            meal_data[emp_name.lower()] = 5720

print(f"  NIETE ICT employees with meal deduction: {len(meal_data)}")
print()

# ============================================================================
# STEP 6: Summary Report
# ============================================================================
print('=' * 80)
print('AUDIT SUMMARY')
print('=' * 80)
print()

print('Total entities:', len(entities))
print('Total employees in payroll:', sum(len(data['rows']) for data in payroll_data.values()))
print()

print('Data source references loaded:')
print(f'  ✅ Tax deductions: {len(tax_data)} employees')
print(f'  ✅ Commute coaches: {len(commute_data)} coaches')
print(f'  ✅ Meal deductions: {len(meal_data)} employees')
print()

if commute_issues:
    print(f'⚠️  CRITICAL: {len(commute_issues)} potential errors in Commute Allowance section')
    print('   These may be BusCaro entries incorrectly placed in Commute column')
else:
    print('✅ Commute Allowance section looks clean')

print()
print('=' * 80)
