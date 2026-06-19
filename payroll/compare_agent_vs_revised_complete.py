#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive comparison: Agent April vs Revised April 2026
Compare all columns across all 5 entities
Generate detailed difference report
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

AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
REVISED_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

# Columns to compare
columns_to_compare = [
    'Employee ID', 'Employee Name', 'Job Title', 'Department', 'CNIC', 'Joining Date',
    'Bank Name', 'Account Number', 'Gross Salary', 'Basic Salary', 'Medical Allowance',
    'Other Allowance', 'Overtime', 'Commute Allowance', 'Pending Dues', 'Total Allowance',
    'Taxable Salary', 'Income Tax', 'Unpaid Days', 'Abhi', 'Advance', 'Loan', 'BusCaro',
    'Lunch Meal', 'EOBI', 'Total Deductions', 'Net Salary April'
]

print('=' * 160)
print('COMPREHENSIVE COMPARISON: AGENT APRIL VS REVISED APRIL 2026')
print('=' * 160)
print()

all_differences = []
total_employees = 0
employees_with_diffs = 0

for entity in entities:
    print(f'Processing {entity}...')
    print()

    # Load Agent data
    agent_result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    agent_values = agent_result.get('values', [])
    if not agent_values:
        print(f'  No Agent data found\n')
        continue

    agent_headers = agent_values[0]
    agent_col_map = {h.strip(): i for i, h in enumerate(agent_headers)}

    # Load Revised data
    revised_result = service.spreadsheets().values().get(
        spreadsheetId=REVISED_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    revised_values = revised_result.get('values', [])
    if not revised_values:
        print(f'  No Revised data found\n')
        continue

    revised_headers = revised_values[0]
    revised_col_map = {h.strip(): i for i, h in enumerate(revised_headers)}

    # Build map of revised employees
    revised_data = {}
    for revised_row in revised_values[1:]:
        emp_name = revised_row[revised_col_map.get('Employee Name', 1)] if revised_col_map.get('Employee Name', 1) < len(revised_row) else ''
        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()
        revised_data[emp_name_lower] = revised_row

    # Compare Agent vs Revised
    entity_diffs = 0
    for agent_row_idx, agent_row in enumerate(agent_values[1:], 2):
        emp_name = agent_row[agent_col_map.get('Employee Name', 1)] if agent_col_map.get('Employee Name', 1) < len(agent_row) else ''
        if not emp_name:
            continue

        total_employees += 1
        emp_name_lower = emp_name.lower()

        if emp_name_lower not in revised_data:
            print(f'  ⚠️  {emp_name} - NOT FOUND in Revised sheet')
            continue

        revised_row = revised_data[emp_name_lower]

        # Compare each column
        row_diffs = {}
        for col_name in columns_to_compare:
            agent_col_idx = agent_col_map.get(col_name, -1)
            revised_col_idx = revised_col_map.get(col_name, -1)

            if agent_col_idx < 0 or revised_col_idx < 0:
                continue

            agent_val = agent_row[agent_col_idx] if agent_col_idx < len(agent_row) else ''
            revised_val = revised_row[revised_col_idx] if revised_col_idx < len(revised_row) else ''

            # Convert to string for comparison
            agent_str = str(agent_val).strip()
            revised_str = str(revised_val).strip()

            if agent_str != revised_str:
                row_diffs[col_name] = {
                    'agent': agent_val,
                    'revised': revised_val
                }

        if row_diffs:
            employees_with_diffs += 1
            entity_diffs += 1
            all_differences.append({
                'entity': entity,
                'name': emp_name,
                'differences': row_diffs
            })

    print(f'  Found {entity_diffs} employees with differences\n')

print()
print('=' * 160)
print('DETAILED DIFFERENCES REPORT')
print('=' * 160)
print()

if all_differences:
    print(f'Total Employees with Differences: {employees_with_diffs}/{total_employees}\n')
    print()

    for idx, diff in enumerate(all_differences[:20], 1):
        clean_name = diff['name'].encode('utf-8', errors='ignore').decode('utf-8')
        print(f'{idx}. {clean_name} ({diff["entity"]})')
        print()

        for col_name, values in diff['differences'].items():
            agent_val = values['agent']
            revised_val = values['revised']
            print(f'   {col_name}:')
            print(f'     Agent:   {agent_val}')
            print(f'     Revised: {revised_val}')
            print()

    if len(all_differences) > 20:
        print(f'\n... and {len(all_differences) - 20} more employees with differences\n')

print()
print('=' * 160)
print('SUMMARY')
print('=' * 160)
print()
print(f'Total Employees Compared: {total_employees}')
print(f'Employees with Differences: {employees_with_diffs}')
print(f'Total Difference Records: {len(all_differences)}')
print()

# Analyze which columns have the most differences
column_diff_count = {}
for diff in all_differences:
    for col_name in diff['differences'].keys():
        column_diff_count[col_name] = column_diff_count.get(col_name, 0) + 1

if column_diff_count:
    print('Columns with Most Differences:')
    sorted_cols = sorted(column_diff_count.items(), key=lambda x: x[1], reverse=True)
    for col_name, count in sorted_cols[:10]:
        print(f'  {col_name}: {count} employees')
    print()

print('[COMPLETE] Comparison finished')
