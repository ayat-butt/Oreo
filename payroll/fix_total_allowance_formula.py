#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix Total Allowance formula in Agent payroll sheet
Correct formula: =J+K+L+M+N+O (Basic + Medical + Other + Overtime + Commute + Pending Dues)
Remove Gross Salary from the calculation
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
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('=' * 120)
print('FIXING TOTAL ALLOWANCE FORMULA')
print('=' * 120)
print()

print('Correct formula: =J+K+L+M+N+O')
print('(Basic + Medical + Other + Overtime + Commute + Pending Dues)')
print()

for entity in entities:
    print(f'{entity}:')

    # Get all data
    result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:P500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    total_allow_idx = col_map.get('Total Allowance', -1)

    if total_allow_idx < 0:
        print('  Total Allowance column not found')
        continue

    col_letter = chr(65 + total_allow_idx) if total_allow_idx < 26 else chr(64 + total_allow_idx // 26) + chr(65 + total_allow_idx % 26)

    batch_requests = []
    formula_count = 0

    # Build formulas for each row
    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if not emp_name:
            continue

        # Create formula for this row
        formula = f'=J{row_idx}+K{row_idx}+L{row_idx}+M{row_idx}+N{row_idx}+O{row_idx}'

        batch_requests.append({
            'range': f'{entity}!{col_letter}{row_idx}',
            'values': [[formula]]
        })
        formula_count += 1

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'USER_ENTERED'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=AGENT_PAYROLL_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  Fixed formula for {formula_count} employees')

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print('[COMPLETE] Total Allowance formula fixed for all entities')
print('Formula: =J+K+L+M+N+O (Basic + Medical + Other + Overtime + Commute + Pending Dues)')
print()
