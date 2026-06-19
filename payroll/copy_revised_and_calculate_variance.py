#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copy Net Salary April from Revised April 2026 sheet
Apply to Agent payroll Net Salary March column (AB)
Calculate variance between Net Salary April (Agent) and Net Salary March (Revised)
Variance = Agent Net Salary April - Revised Net Salary April
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
print('COPY REVISED APRIL NET SALARY AND CALCULATE VARIANCE')
print('=' * 120)
print()

# Revised April 2026 sheet (original payroll)
REVISED_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'
AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('STEP 1: LOAD NET SALARY APRIL FROM REVISED SHEET')
print('-' * 120)
print()

revised_net_salary = {}

for entity in entities:
    print(f'{entity}:')

    result = service.spreadsheets().values().get(
        spreadsheetId=REVISED_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    net_salary_idx = col_map.get('Net Salary April', -1)

    if net_salary_idx < 0:
        print('  Net Salary April column not found')
        continue

    entity_count = 0
    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        net_sal = row[net_salary_idx] if net_salary_idx < len(row) else ''

        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()
        revised_net_salary[emp_name_lower] = {
            'entity': entity,
            'net_salary': net_sal,
            'row_idx': row_idx
        }
        entity_count += 1

    print(f'  Loaded {entity_count} employees')
    print()

print(f'Total employees loaded from revised sheet: {len(revised_net_salary)}')
print()

total_copied = 0
total_variance = 0

print('=' * 120)
print('STEP 2: COPY TO AGENT SHEET NET SALARY MARCH COLUMN AND CALCULATE VARIANCE')
print('-' * 120)
print()

for entity in entities:
    print(f'{entity}:')

    result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:AI500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    net_salary_march_idx = col_map.get('Net Salary March', -1)  # Column AB (27)
    net_salary_april_idx = col_map.get('Net Salary April', -1)   # Column AA (26)
    variance_idx = col_map.get('Variance', -1)                   # Column AC (28)

    if net_salary_march_idx < 0:
        print('  Net Salary March column not found')
        continue

    if net_salary_april_idx < 0:
        print('  Net Salary April column not found')
        continue

    batch_requests = []
    entity_copied = 0
    entity_variance = 0

    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        emp_name_lower = emp_name.lower()

        if not emp_name or emp_name_lower not in revised_net_salary:
            continue

        revised_net_sal = revised_net_salary[emp_name_lower]['net_salary']

        # Copy Revised Net Salary April to Agent Net Salary March column
        march_col_letter = chr(65 + net_salary_march_idx) if net_salary_march_idx < 26 else chr(64 + net_salary_march_idx // 26) + chr(65 + net_salary_march_idx % 26)
        batch_requests.append({
            'range': f'{entity}!{march_col_letter}{row_idx}',
            'values': [[revised_net_sal]]
        })

        # Calculate Variance = Agent Net Salary April - Revised Net Salary April
        agent_net_sal = row[net_salary_april_idx] if net_salary_april_idx < len(row) else ''

        try:
            revised_num = float(str(revised_net_sal).replace(',', '').strip()) if revised_net_sal else 0
            agent_num = float(str(agent_net_sal).replace(',', '').strip()) if agent_net_sal else 0
            variance = agent_num - revised_num
        except:
            variance = 0

        # Add variance to batch if Variance column exists
        if variance_idx >= 0:
            var_col_letter = chr(65 + variance_idx) if variance_idx < 26 else chr(64 + variance_idx // 26) + chr(65 + variance_idx % 26)
            batch_requests.append({
                'range': f'{entity}!{var_col_letter}{row_idx}',
                'values': [[variance]]
            })
            entity_variance += 1

        entity_copied += 1

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=AGENT_PAYROLL_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  Copied Net Salary: {entity_copied} employees')
        print(f'  Calculated Variance: {entity_variance} employees')
        total_copied += entity_copied
        total_variance += entity_variance

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print(f'Revised April Net Salary loaded: {len(revised_net_salary)} employees')
print(f'Copied to Agent Net Salary March column: {total_copied} employees')
print(f'Variance calculated (Agent Apr - Revised Apr): {total_variance} employees')
print()
print('[COMPLETE] Revised April net salary applied and variance calculated')
print()
