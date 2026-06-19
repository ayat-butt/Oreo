#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Identify and get details of the 3-4 new joiners not in Revised sheet
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

print('=' * 120)
print('DETAILS OF NEW JOINERS (NOT IN REVISED SHEET)')
print('=' * 120)
print()

new_joiners = [
    ('NIETE_Islamabad', 'Sumaya Imran'),
    ('OPL', 'Zeest Hassan Qureshi'),
    ('OWT', 'Razia Kausar'),
    ('OWT', 'Ayesha Jamshaid')
]

for entity, emp_name in new_joiners:
    print(f'{emp_name} ({entity})')
    print()

    result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found\n')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    emp_id_idx = col_map.get('Employee ID', 0)
    job_title_idx = col_map.get('Job Title', -1)
    department_idx = col_map.get('Department', -1)
    joining_date_idx = col_map.get('Joining Date', -1)
    gross_idx = col_map.get('Gross Salary', -1)
    cnic_idx = col_map.get('CNIC', -1)
    bank_idx = col_map.get('Bank Name', -1)

    found = False
    for row in values[1:]:
        row_name = row[name_idx] if name_idx < len(row) else ''
        if row_name.lower() == emp_name.lower():
            found = True

            emp_id = row[emp_id_idx] if emp_id_idx >= 0 and emp_id_idx < len(row) else ''
            job_title = row[job_title_idx] if job_title_idx >= 0 and job_title_idx < len(row) else ''
            department = row[department_idx] if department_idx >= 0 and department_idx < len(row) else ''
            joining_date = row[joining_date_idx] if joining_date_idx >= 0 and joining_date_idx < len(row) else ''
            gross_sal = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
            cnic = row[cnic_idx] if cnic_idx >= 0 and cnic_idx < len(row) else ''
            bank = row[bank_idx] if bank_idx >= 0 and bank_idx < len(row) else ''

            print(f'  Employee ID: {emp_id}')
            print(f'  Job Title: {job_title}')
            print(f'  Department: {department}')
            print(f'  Joining Date: {joining_date}')
            print(f'  Gross Salary: {gross_sal}')
            print(f'  CNIC: {cnic}')
            print(f'  Bank: {bank}')
            print()

            break

    if not found:
        print(f'  NOT FOUND in Agent payroll\n')

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print('These 4 employees are in Agent April payroll but NOT in Revised April 2026 sheet.')
print('They are likely new joiners who joined in April 2026 or after Revised sheet was created.')
print()
print('For these new joiners:')
print('  - They have no YTD Taxable (Jul-Feb) historical data')
print('  - Their Annual Tax Liability needs to be calculated based on April salary only')
print('  - Their Income Tax should be based on their April taxable salary with Pakistan tax slabs')
print()
