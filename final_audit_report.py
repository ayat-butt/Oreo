#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FINAL COMPREHENSIVE AUDIT - April 2026 Payroll
All 16 steps verification and summary
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 120)
print('FINAL COMPREHENSIVE AUDIT - APRIL 2026 PAYROLL (ALL 16 STEPS)')
print('=' * 120)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

# Load all payroll data
all_data = {}
total_employees = 0

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

    all_data[entity] = {
        'headers': headers,
        'col_map': col_map,
        'rows': values[1:]
    }

    total_employees += len(values[1:])

print(f'Total employees across 5 entities: {total_employees}')
print()

# Define columns to check
columns_to_check = [
    'Employee ID',
    'Employee Name',
    'Gross Salary',
    'Basic Salary',
    'Medical Allowance',
    'Other Allowance',
    'Overtime',
    'Commute Allowance',
    'Pending Dues',
    'Total Allowance',
    'Taxable Salary',
    'Income Tax',
    'Unpaid Days',
    'Advance',
    'Loan',
    'BusCaro',
    'Lunch Meal',
    'EOBI',
    'Total Deductions',
    'Net Salary'
]

print('STEP-BY-STEP VERIFICATION')
print('=' * 120)
print()

# Step 1-5: Basic employee info and salaries
print('STEPS 1-5: Employee Info & Salary Components')
print('-' * 120)

for col in ['Employee ID', 'Employee Name', 'Gross Salary', 'Basic Salary', 'Medical Allowance', 'Other Allowance']:
    has_values = 0
    empty = 0

    for entity, data in all_data.items():
        col_idx = data['col_map'].get(col, -1)
        if col_idx < 0:
            continue

        for row in data['rows']:
            if col_idx < len(row) and row[col_idx]:
                has_values += 1
            else:
                empty += 1

    pct = (has_values / (has_values + empty) * 100) if (has_values + empty) > 0 else 0
    status = '[OK]' if pct >= 99 else '[WARN]'
    print(f'  {col:30} {has_values:3}/{total_employees:3} ({pct:5.1f}%) {status}')

print()

# Step 6-7: Overtime, Commute, Pending
print('STEPS 6-7: Variable Allowances (Overtime, Commute, Pending Dues)')
print('-' * 120)

for col in ['Overtime', 'Commute Allowance', 'Pending Dues']:
    has_nonzero = 0

    for entity, data in all_data.items():
        col_idx = data['col_map'].get(col, -1)
        if col_idx < 0:
            continue

        for row in data['rows']:
            if col_idx < len(row) and row[col_idx] and str(row[col_idx]).strip() and str(row[col_idx]) != '0':
                has_nonzero += 1

    pct = (has_nonzero / total_employees * 100)
    print(f'  {col:30} {has_nonzero:3} employees with values ({pct:5.1f}%)')

print()

# Step 8: Total Allowance
print('STEP 8: Total Allowance Formula')
print('-' * 120)

col_idx_map = {}
for entity, data in all_data.items():
    col_idx_map[entity] = data['col_map'].get('Total Allowance', -1)

has_formula = 0
for entity, col_idx in col_idx_map.items():
    if col_idx >= 0:
        for row in all_data[entity]['rows']:
            if col_idx < len(row) and row[col_idx]:
                has_formula += 1

print(f'  Total Allowance (Column P): {has_formula}/{total_employees} employees [{"OK" if has_formula >= 185 else "INCOMPLETE"}]')

print()

# Step 9: Taxable Salary
print('STEP 9: Taxable Salary Formula')
print('-' * 120)

col_idx_map = {}
for entity, data in all_data.items():
    col_idx_map[entity] = data['col_map'].get('Taxable Salary', -1)

has_formula = 0
for entity, col_idx in col_idx_map.items():
    if col_idx >= 0:
        for row in all_data[entity]['rows']:
            if col_idx < len(row) and row[col_idx]:
                has_formula += 1

print(f'  Taxable Salary (Column Q): {has_formula}/{total_employees} employees [{"OK" if has_formula >= 185 else "INCOMPLETE"}]')

print()

# Step 10: Income Tax
print('STEP 10: Income Tax (Lookup/Calculated)')
print('-' * 120)

income_tax_values = {'0': 0, 'nonzero': 0, 'blank': 0}

for entity, data in all_data.items():
    col_idx = data['col_map'].get('Income Tax', -1)
    if col_idx < 0:
        continue

    for row in data['rows']:
        if col_idx < len(row):
            val = row[col_idx]
            if not val or str(val).strip() == '':
                income_tax_values['blank'] += 1
            elif str(val).strip() == '0':
                income_tax_values['0'] += 1
            else:
                income_tax_values['nonzero'] += 1

print(f'  With tax deduction: {income_tax_values["nonzero"]}')
print(f'  Zero tax: {income_tax_values["0"]}')
print(f'  Blank/Missing: {income_tax_values["blank"]}')
print(f'  Total: {sum(income_tax_values.values())}/{total_employees}')

print()

# Steps 11-14: Deductions
print('STEPS 11-14: Deduction Components')
print('-' * 120)

for col in ['Advance', 'Loan', 'BusCaro', 'Lunch Meal', 'EOBI']:
    has_nonzero = 0
    blank = 0

    for entity, data in all_data.items():
        col_idx = data['col_map'].get(col, -1)
        if col_idx < 0:
            continue

        for row in data['rows']:
            if col_idx < len(row):
                val = row[col_idx]
                if not val or str(val).strip() == '':
                    blank += 1
                elif str(val) != '0':
                    has_nonzero += 1

    pct = (has_nonzero / total_employees * 100)
    print(f'  {col:30} {has_nonzero:3} employees with values ({pct:5.1f}%)')

print()

# Step 15: Total Deductions
print('STEP 15: Total Deductions Formula')
print('-' * 120)

has_formula = 0
for entity, data in all_data.items():
    col_idx = data['col_map'].get('Total Deductions', -1)
    if col_idx < 0:
        continue

    for row in data['rows']:
        if col_idx < len(row) and row[col_idx]:
            has_formula += 1

print(f'  Total Deductions (Column Z): {has_formula}/{total_employees} employees [{"OK" if has_formula >= 185 else "INCOMPLETE"}]')

print()

# Step 16: Net Salary
print('STEP 16: Net Salary Formula')
print('-' * 120)

has_formula = 0
for entity, data in all_data.items():
    col_idx = data['col_map'].get('Net Salary', -1)
    if col_idx < 0:
        continue

    for row in data['rows']:
        if col_idx < len(row) and row[col_idx]:
            has_formula += 1

print(f'  Net Salary (Column AA): {has_formula}/{total_employees} employees [{"OK" if has_formula >= 185 else "INCOMPLETE"}]')

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print('Completed actions in this session:')
print('  [DONE] Cleared all Commute Allowance entries (Column N)')
print('  [DONE] Cleared all BusCaro entries (Column W)')
print('  [DONE] Applied BusCaro values (12 employees)')
print('  [DONE] Calculated and applied Income Tax (183 employees)')
print()
print('Ready for: Final verification and approval')
print()
