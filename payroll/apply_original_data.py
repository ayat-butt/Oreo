#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Apply original April payroll data to Agent payroll sheet
Compare and apply: Overtime, Commute, Pending Dues, Abhi, Advance, Loan, BusCaro, Lunch
DO NOT MODIFY: Income Tax values
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
print('APPLYING ORIGINAL APRIL PAYROLL DATA TO AGENT PAYROLL')
print('=' * 120)
print()

# Load original data
with open('original_april_data.json', 'r') as f:
    original_data = json.load(f)

print(f'Loaded original data for {sum(len(e) for e in original_data.values())} employees')
print()

# Current Agent payroll
AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

# Columns to apply
columns_to_apply = ['Overtime', 'Commute Allowance', 'Pending Dues', 'Abhi', 'Advance', 'Loan', 'BusCaro', 'Lunch Meal']

print('APPLYING DATA TO AGENT PAYROLL')
print('-' * 120)
print()

total_applied = 0
differences = []

for entity in entities:
    print(f'{entity}:')

    # Load Agent payroll
    result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    agent_values = result.get('values', [])
    if not agent_values:
        print('  No data found')
        continue

    headers = agent_values[0]
    col_map = {h: i for i, h in enumerate(headers)}

    # Build batch update for columns to apply
    batch_requests = []
    entity_applied = 0

    for row_idx, row in enumerate(agent_values[1:], 2):
        emp_name = row[col_map.get('Employee Name', 1)] if col_map.get('Employee Name', 1) < len(row) else ''
        emp_name_lower = emp_name.lower()

        # Check if employee exists in original data
        if entity in original_data and emp_name_lower in original_data[entity]:
            original_emp = original_data[entity][emp_name_lower]

            # Apply each column
            for col_name in columns_to_apply:
                col_idx = col_map.get(col_name, -1)
                if col_idx < 0:
                    continue

                original_val = original_emp.get(col_name, '')
                current_val = row[col_idx] if col_idx < len(row) else ''

                # Only apply if different
                if str(original_val).strip() != str(current_val).strip():
                    batch_requests.append({
                        'range': f'{entity}!{chr(65 + col_idx)}{row_idx}',
                        'values': [[original_val]]
                    })

                    # Track difference
                    if emp_name not in [d['name'] for d in differences]:
                        differences.append({
                            'entity': entity,
                            'name': emp_name,
                            'changes': {}
                        })

                    for d in differences:
                        if d['name'] == emp_name:
                            d['changes'][col_name] = {
                                'original': original_val,
                                'agent': current_val
                            }

            entity_applied += len(batch_requests)

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=AGENT_PAYROLL_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  Applied {updated} changes to {len(set(r["range"].split("!")[1][:-1] for r in batch_requests))} employees')
        total_applied += updated

print()
print('=' * 120)
print('DIFFERENCES FOUND')
print('=' * 120)
print()

if differences:
    print(f'Total employees with differences: {len(differences)}')
    print()

    # Show first 10 differences
    for diff_idx, diff in enumerate(differences[:10], 1):
        clean_name = diff['name'].encode('utf-8', errors='ignore').decode('utf-8')
        print(f'{diff_idx}. {clean_name} ({diff["entity"]}):')

        for col_name, values in diff['changes'].items():
            orig = values['original']
            curr = values['agent']
            print(f'   {col_name:20} Original: {str(orig):15} → Agent: {str(curr):15}')

        print()

    if len(differences) > 10:
        print(f'... and {len(differences) - 10} more employees with differences')
        print()
else:
    print('No differences found - all data matches original!')
    print()

print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print(f'Total changes applied: {total_applied}')
print(f'Employees with updates: {len(differences)}')
print()
print('[COMPLETE] Original April payroll data applied to Agent payroll')
print()
