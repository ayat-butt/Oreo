#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Load data from original April 2026 payroll sheet
Extract: Additions/Deletions, Commute, Pending Dues, Overtime, Abhi, Loans, Advances, BusCaro, Lunch
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
print('LOADING ORIGINAL APRIL 2026 PAYROLL SHEET')
print('=' * 120)
print()

ORIGINAL_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'

# Get metadata to see available tabs
metadata = service.spreadsheets().get(spreadsheetId=ORIGINAL_SHEET_ID).execute()
tabs = [s['properties']['title'] for s in metadata['sheets']]

print(f'Available tabs in original sheet: {", ".join(tabs[:5])}...')
print()

# Load data from each entity
original_data = {}
entities_to_load = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('EXTRACTING DATA FROM ORIGINAL SHEET')
print('-' * 120)
print()

for entity in entities_to_load:
    if entity not in tabs:
        print(f'{entity}: Not found in original sheet')
        continue

    print(f'{entity}:')

    result = service.spreadsheets().values().get(
        spreadsheetId=ORIGINAL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print(f'  No data found')
        continue

    headers = values[0]
    col_map = {h: i for i, h in enumerate(headers)}

    # Columns to extract
    columns_needed = [
        'Employee ID', 'Employee Name', 'Gross Salary',
        'Overtime', 'Commute Allowance', 'Pending Dues',
        'Abhi', 'Advance', 'Loan', 'BusCaro', 'Lunch Meal'
    ]

    # Build map of available columns
    available_cols = {col: col_map.get(col, -1) for col in columns_needed}

    print(f'  Headers found: {sum(1 for v in available_cols.values() if v >= 0)}/{len(columns_needed)}')

    # Extract data for each employee
    entity_data = {}
    for row_idx, row in enumerate(values[1:], 2):
        emp_id = row[col_map.get('Employee ID', -1)] if col_map.get('Employee ID', -1) >= 0 and col_map.get('Employee ID', -1) < len(row) else ''
        emp_name = row[col_map.get('Employee Name', -1)] if col_map.get('Employee Name', -1) >= 0 and col_map.get('Employee Name', -1) < len(row) else ''

        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()

        # Extract all columns for this employee
        employee_record = {
            'name': emp_name,
            'entity': entity,
            'row': row_idx
        }

        for col_name in columns_needed:
            col_idx = available_cols[col_name]
            if col_idx >= 0 and col_idx < len(row):
                employee_record[col_name] = row[col_idx]
            else:
                employee_record[col_name] = ''

        entity_data[emp_name_lower] = employee_record

    original_data[entity] = entity_data
    print(f'  Extracted {len(entity_data)} employees')
    print()

print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()

total_employees = sum(len(data) for data in original_data.values())
print(f'Total employees in original sheet: {total_employees}')
print()

# Show sample data
print('Sample data from original sheet (first 3 employees):')
print('-' * 120)
print()

sample_count = 0
for entity, employees in original_data.items():
    for emp_name_lower, emp_data in employees.items():
        if sample_count >= 3:
            break

        clean_name = emp_data['name'].encode('utf-8', errors='ignore').decode('utf-8')
        print(f'{clean_name} ({entity}):')
        print(f'  Overtime: {emp_data.get("Overtime", "")}')
        print(f'  Commute: {emp_data.get("Commute Allowance", "")}')
        print(f'  Pending Dues: {emp_data.get("Pending Dues", "")}')
        print(f'  Advance: {emp_data.get("Advance", "")}')
        print(f'  Loan: {emp_data.get("Loan", "")}')
        print(f'  BusCaro: {emp_data.get("BusCaro", "")}')
        print(f'  Lunch: {emp_data.get("Lunch Meal", "")}')
        print()
        sample_count += 1

# Save to file
with open('original_april_data.json', 'w') as f:
    json.dump(original_data, f, indent=2)

print('[OK] Saved original data to: original_april_data.json')
print()
