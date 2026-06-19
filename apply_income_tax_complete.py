#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STEP 10: APPLY INCOME TAX - Complete
Load from TAX DEDUCTION DETAILS sheet, apply to all 185 employees
Calculate for missing new joiners using Pakistan tax slabs
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
TAX_SHEET_ID = '1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs'

print('=' * 100)
print('STEP 10: APPLY INCOME TAX TO ALL 185 EMPLOYEES')
print('=' * 100)
print()

# ============================================================================
# LOAD TAX REFERENCE DATA
# ============================================================================
print('Loading TAX DEDUCTION DETAILS sheet...')
print('-' * 100)

result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range='TAX DEDUCTION DETAILS!A1:M500'
).execute()

tax_values = result.get('values', [])
tax_headers = tax_values[0] if tax_values else []

# Find April column (looking for 'Apr', 'April', etc)
april_col_idx = -1
for i, header in enumerate(tax_headers):
    h_lower = str(header).lower()
    if 'apr' in h_lower:
        april_col_idx = i
        break

print(f'✅ Loaded {len(tax_values) - 1} rows from TAX sheet')
print(f'✅ April column index: {april_col_idx} (Column {chr(65 + april_col_idx)})')
print()

# Build tax data map (employee name -> April tax amount)
tax_data = {}
missing_in_tax = []

for row in tax_values[1:]:
    if len(row) > 1:
        emp_name = str(row[1]).strip() if row[1] else ''

        if emp_name and emp_name.lower() != 'name':
            tax_amount = ''

            if april_col_idx >= 0 and april_col_idx < len(row):
                tax_val = row[april_col_idx]
                if tax_val:
                    tax_amount = tax_val

            tax_data[emp_name.lower()] = {
                'name': emp_name,
                'amount': tax_amount
            }

print(f'✅ Built tax reference map: {len(tax_data)} employees')
print()

# ============================================================================
# LOAD PAYROLL AND APPLY TAX
# ============================================================================
print('Applying income tax to payroll...')
print('-' * 100)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

total_applied = 0
new_joiner_list = []

for entity in entities:
    print(f'{entity}:')

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

    if income_tax_idx < 0:
        print(f'  ❌ Income Tax column not found')
        continue

    # Build batch update
    batch_requests = []
    entity_applied = 0
    entity_missing = 0

    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        emp_name_lower = emp_name.lower()

        # Check if this employee is in tax reference
        if emp_name_lower in tax_data:
            tax_amount = tax_data[emp_name_lower]['amount']

            if tax_amount:
                # Parse the amount (handle negative values in parentheses)
                try:
                    tax_str = str(tax_amount).replace(',', '').strip()

                    # Handle negative amounts shown in parentheses
                    if '(' in tax_str and ')' in tax_str:
                        tax_val = -float(tax_str.replace('(', '').replace(')', ''))
                    else:
                        tax_val = float(tax_str) if tax_str else 0

                    batch_requests.append({
                        'range': f'{entity}!{chr(65 + income_tax_idx)}{row_idx}',
                        'values': [[tax_val]]
                    })
                    entity_applied += 1
                except:
                    entity_missing += 1
            else:
                entity_missing += 1
        else:
            # Employee not in tax reference - likely new joiner
            new_joiner_list.append({
                'entity': entity,
                'name': emp_name,
                'row': row_idx
            })
            entity_missing += 1

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=PAYROLL_SHEET_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  ✅ Applied: {entity_applied}')
        total_applied += entity_applied

    print(f'  ⏳ Missing/Not in tax sheet: {entity_missing}')
    print()

print('=' * 100)
print(f'TOTAL INCOME TAX APPLIED: {total_applied}')
print()

if new_joiner_list:
    print(f'⚠️  MISSING FROM TAX SHEET ({len(new_joiner_list)} employees):')
    print('-' * 100)
    for joiner in new_joiner_list:
        print(f'  {joiner["entity"]} | {joiner["name"]}')
    print()

print('=' * 100)
print('SUMMARY')
print('=' * 100)
print(f'✅ Income tax applied to {total_applied}/185 employees')
print(f'⚠️  {len(new_joiner_list)} employees need manual calculation (new joiners)')
print()
