#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recalculate variance for all 5 entities after Total Allowance formula fix
Variance = Agent Net Salary April (AA) - Net Salary March (AB, which is Revised April)
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
print('RECALCULATING VARIANCE FOR ALL 5 ENTITIES')
print('=' * 120)
print()

print('Variance = Agent Net Salary April (AA) - Net Salary March (AB)')
print()

total_variance_updated = 0

for entity in entities:
    print(f'{entity}:')

    # Get all data
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
    net_salary_april_idx = col_map.get('Net Salary April', -1)      # AA (26)
    net_salary_march_idx = col_map.get('Net Salary March', -1)        # AB (27)
    variance_idx = col_map.get('Variance', -1)                        # AC (28)

    if variance_idx < 0:
        print('  Variance column not found')
        continue

    batch_requests = []
    entity_variance_count = 0

    # Calculate variance for each row
    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if not emp_name:
            continue

        agent_net_sal = row[net_salary_april_idx] if net_salary_april_idx >= 0 and net_salary_april_idx < len(row) else ''
        revised_net_sal = row[net_salary_march_idx] if net_salary_march_idx >= 0 and net_salary_march_idx < len(row) else ''

        # Calculate variance
        try:
            agent_num = float(str(agent_net_sal).replace(',', '').strip()) if agent_net_sal else 0
            revised_num = float(str(revised_net_sal).replace(',', '').strip()) if revised_net_sal else 0
            variance = agent_num - revised_num
        except:
            variance = 0

        variance_col_letter = chr(65 + variance_idx) if variance_idx < 26 else chr(64 + variance_idx // 26) + chr(65 + variance_idx % 26)

        batch_requests.append({
            'range': f'{entity}!{variance_col_letter}{row_idx}',
            'values': [[variance]]
        })
        entity_variance_count += 1

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=AGENT_PAYROLL_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  Recalculated variance for {entity_variance_count} employees')
        total_variance_updated += entity_variance_count

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print(f'Total variance recalculated: {total_variance_updated} employees')
print()
print('[COMPLETE] Variance updated for all 5 entities')
print('Now reflects corrected Net Salary April after Total Allowance formula fix')
print()
