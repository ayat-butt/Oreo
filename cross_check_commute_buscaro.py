#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CROSS-CHECK: Commute Allowance vs BusCaro
Verify payroll entries against source sheets
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
COMMUTE_SHEET_ID = '10kM4xcC0S7nSJhU5HfH6ZdbiTxqyzw5P4_z5nOJ7lck'
BUSCARO_SHEET_ID = '12EyDg8UAuDFexpJ_oC7hCN2HU0lDuQbAHHkmbdFKJwQ'

print('=' * 100)
print('CROSS-CHECK: COMMUTE ALLOWANCE vs BusCARO')
print('=' * 100)
print()

# ============================================================================
# STEP 1: Load Commute Allowance Sheet
# ============================================================================
print('LOADING COMMUTE ALLOWANCE SHEET...')
print('-' * 100)

try:
    result = service.spreadsheets().values().get(
        spreadsheetId=COMMUTE_SHEET_ID,
        range="'April 2026'!A1:E100"
    ).execute()

    commute_values = result.get('values', [])
    print(f'✅ Loaded {len(commute_values)} rows from Commute sheet (April 2026 tab)')

    # Build commute data map
    commute_data = {}
    for row in commute_values[1:]:
        if len(row) > 1:
            emp_name = str(row[1]).strip().lower() if len(row) > 1 and row[1] else ''
            amount = row[3] if len(row) > 3 and row[3] else ''
            if emp_name and amount:
                commute_data[emp_name] = {
                    'amount': amount,
                    'raw_name': row[1] if len(row) > 1 else ''
                }

    print(f'✅ Found {len(commute_data)} employees with commute allowance')
    print()

except Exception as e:
    print(f'❌ ERROR loading Commute sheet: {e}')
    print()

# ============================================================================
# STEP 2: Load BusCaro Sheet
# ============================================================================
print('LOADING BUSCARO SHEET...')
print('-' * 100)

try:
    result = service.spreadsheets().values().get(
        spreadsheetId=BUSCARO_SHEET_ID,
        range="'April 2026'!A1:F200"
    ).execute()

    buscaro_values = result.get('values', [])
    print(f'✅ Loaded {len(buscaro_values)} rows from BusCaro sheet (April 2026 tab)')

    # Build buscaro data map - key by USER column (blue highlighted)
    # Need to find USER column first
    buscaro_headers = buscaro_values[0] if buscaro_values else []
    user_col_idx = -1
    for i, h in enumerate(buscaro_headers):
        if 'user' in str(h).lower():
            user_col_idx = i
            break

    if user_col_idx < 0:
        # Try column D as default
        user_col_idx = 3

    buscaro_data = {}
    for row in buscaro_values[1:]:
        if len(row) > user_col_idx:
            emp_name = str(row[user_col_idx]).strip().lower() if row[user_col_idx] else ''
            amount = row[len(row) - 1] if len(row) > 0 else ''  # Last column usually has amount

            # Try to get amount from rightmost non-empty column
            for i in range(len(row) - 1, -1, -1):
                try:
                    amt = float(str(row[i]).replace(',', '').replace('(', '').replace(')', ''))
                    if amt > 0:
                        amount = row[i]
                        break
                except:
                    pass

            if emp_name and amount:
                buscaro_data[emp_name] = {
                    'amount': amount,
                    'raw_name': row[user_col_idx] if user_col_idx < len(row) else ''
                }

    print(f'✅ Found {len(buscaro_data)} entries in BusCaro sheet')
    print()

except Exception as e:
    print(f'❌ ERROR loading BusCaro sheet: {e}')
    print()

# ============================================================================
# STEP 3: Load Current Payroll
# ============================================================================
print('LOADING CURRENT PAYROLL...')
print('-' * 100)

payroll_data = {}
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

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

    payroll_data[entity] = {
        'headers': headers,
        'name_idx': name_idx,
        'commute_idx': commute_idx,
        'buscaro_idx': buscaro_idx,
        'rows': values[1:]
    }

print(f'✅ Loaded payroll for {len(entities)} entities')
print()

# ============================================================================
# STEP 4: Cross-check Commute Allowance in Payroll
# ============================================================================
print('CROSS-CHECK: COMMUTE ALLOWANCE ENTRIES IN PAYROLL')
print('=' * 100)

commute_mismatches = []

for entity, data in payroll_data.items():
    if data['commute_idx'] < 0:
        continue

    print(f'\n{entity.upper()}:')
    print('-' * 100)

    entity_commute_count = 0
    for row_idx, row in enumerate(data['rows']):
        emp_name = row[data['name_idx']] if data['name_idx'] < len(row) else ''
        commute_val = row[data['commute_idx']] if data['commute_idx'] < len(row) else ''

        if commute_val and str(commute_val).strip() and str(commute_val) != '0':
            clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
            emp_name_lower = clean_name.lower()

            # Check if this employee is in the Commute source sheet
            if emp_name_lower in commute_data:
                print(f"  ✅ {clean_name} = {commute_val} [VERIFIED in source sheet]")
                entity_commute_count += 1
            else:
                # This entry is NOT in the source sheet - it's wrong!
                print(f"  ⚠️  {clean_name} = {commute_val} [NOT in Commute source sheet]")

                # Is it in BusCaro instead?
                if emp_name_lower in buscaro_data:
                    buscaro_amt = buscaro_data[emp_name_lower]['amount']
                    print(f"       → FOUND in BusCaro sheet with amount: {buscaro_amt}")
                    print(f"       → This should be in Column W (BusCaro), NOT Column N (Commute)")

                commute_mismatches.append({
                    'entity': entity,
                    'name': clean_name,
                    'commute_val': commute_val,
                    'in_buscaro': emp_name_lower in buscaro_data
                })
                entity_commute_count += 1

    print(f'  Total: {entity_commute_count} entries checked')

print()
print('=' * 100)
print('SUMMARY')
print('=' * 100)
print()

if commute_mismatches:
    print(f'🔴 FOUND {len(commute_mismatches)} WRONG ENTRIES IN COMMUTE ALLOWANCE COLUMN:')
    print()

    for mismatch in commute_mismatches:
        status = "ALSO in BusCaro" if mismatch['in_buscaro'] else "Not found in any source"
        print(f"  • {mismatch['entity']} | {mismatch['name']} = {mismatch['commute_val']} ({status})")
else:
    print('✅ All commute allowance entries verified against source sheet')

print()
print('Commute Allowance source data found:', len(commute_data), 'employees')
print('BusCaro source data found:', len(buscaro_data), 'entries')
print()
