#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEBUG: Name matching between payroll and tax sheet
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

# Load tax sheet
result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range='TAX DEDUCTION DETAILS!A1:M500'
).execute()

tax_values = result.get('values', [])
tax_names = set()

for row in tax_values[1:]:
    if len(row) > 1 and row[1]:
        emp_name = str(row[1]).strip()
        tax_names.add(emp_name.lower())

print(f'Tax sheet has {len(tax_names)} unique employee names')
print()
print('Sample from tax sheet (first 20):')
for i, name in enumerate(sorted(list(tax_names))[:20]):
    print(f'  {name}')

print()
print('=' * 100)
print('PAYROLL NAMES vs TAX SHEET NAMES')
print('=' * 100)
print()

# Load NIETE_Islamabad payroll
result = service.spreadsheets().values().get(
    spreadsheetId=PAYROLL_SHEET_ID,
    range='NIETE_Islamabad!A1:AA500'
).execute()

values = result.get('values', [])
headers = values[0]
name_idx = headers.index('Employee Name') if 'Employee Name' in headers else 1

payroll_names = []
for row in values[1:]:
    if len(row) > name_idx and row[name_idx]:
        emp_name = str(row[name_idx]).strip()
        payroll_names.append(emp_name)

print(f'Payroll has {len(payroll_names)} employee names')
print()
print('Sample from payroll (first 10):')
for name in payroll_names[:10]:
    clean = name.encode('utf-8', errors='ignore').decode('utf-8')
    print(f'  "{clean}"')

print()
print('Checking matches (first 20 payroll employees):')
print('-' * 100)

matched = 0
not_matched = []

for name in payroll_names[:20]:
    name_lower = name.lower()
    clean = name.encode('utf-8', errors='ignore').decode('utf-8')

    if name_lower in tax_names:
        print(f'  ✅ {clean}')
        matched += 1
    else:
        print(f'  ❌ {clean} [NOT FOUND in tax sheet]')
        not_matched.append(clean)

print()
print(f'Matched: {matched}/20')
print()

if not_matched:
    print('Checking if close matches exist in tax sheet:')
    for pname in not_matched:
        # Try to find similar names
        similar = [tname for tname in tax_names if pname.split()[0].lower() in tname or
                   (len(pname.split()) > 1 and pname.split()[-1].lower() in tname)]

        if similar:
            print(f'  {pname}:')
            for s in similar[:3]:
                print(f'    → {s}')
