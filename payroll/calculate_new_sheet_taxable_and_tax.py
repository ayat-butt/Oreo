#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculate Taxable Salary and Income Tax for the new payroll sheet
Taxable Salary = Total Allowance - Medical Allowance - Unpaid Days
Income Tax = Load from Revised April sheet or calculate using financial year method
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

NEW_SHEET_ID = '14Ht2gr3YCwaDzJVDvHzEIYhMY-Q89QpgkNvzwKSAkLA'
REVISED_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('=' * 120)
print('CALCULATING TAXABLE SALARY AND INCOME TAX FOR NEW SHEET')
print('=' * 120)
print()

# First, load income tax data from Revised April sheet
print('STEP 1: Loading Income Tax data from Revised April sheet...')
print()

revised_tax_data = {}

for entity in entities:
    result = service.spreadsheets().values().get(
        spreadsheetId=REVISED_SHEET_ID,
        range=f'{entity}!A1:R500'
    ).execute()

    values = result.get('values', [])
    if not values:
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    income_tax_idx = col_map.get('Income Tax', -1)
    annual_tax_idx = col_map.get('Annual Tax Liability (FBR)', -1)
    tax_collected_idx = col_map.get('Tax Collected So Far (Jul–Feb)', -1)

    for row in values[1:]:
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()

        # Prefer using formula data if available, otherwise use direct income tax
        if annual_tax_idx >= 0 and tax_collected_idx >= 0:
            annual_tax = row[annual_tax_idx] if annual_tax_idx < len(row) else ''
            tax_collected = row[tax_collected_idx] if tax_collected_idx < len(row) else ''

            try:
                annual_tax_num = float(str(annual_tax).replace(',', '').strip()) if annual_tax else 0
                tax_collected_num = float(str(tax_collected).replace(',', '').strip()) if tax_collected else 0
                calc_tax = (annual_tax_num - tax_collected_num) / 4
            except:
                calc_tax = 0
        else:
            income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''
            try:
                calc_tax = float(str(income_tax).replace(',', '').strip()) if income_tax else 0
            except:
                calc_tax = 0

        revised_tax_data[emp_name_lower] = calc_tax

print(f'Loaded income tax data for {len(revised_tax_data)} employees from Revised sheet')
print()

print('=' * 120)
print('STEP 2: Calculating Taxable Salary and Income Tax for new sheet...')
print('=' * 120)
print()

total_processed = 0
total_taxable_calcs = 0
total_income_tax_calcs = 0

for entity in entities:
    print(f'{entity}:')

    # Load new sheet data
    result = service.spreadsheets().values().get(
        spreadsheetId=NEW_SHEET_ID,
        range=f'{entity}!A1:AJ500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found\n')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    total_allow_idx = col_map.get('Total Allowance', -1)
    medical_idx = col_map.get('Medical Allowance', -1)
    unpaid_idx = col_map.get('Unpaid Days', -1)

    # Different column names for Taxable Salary
    taxable_idx = col_map.get('Taxable Salary', -1)
    if taxable_idx < 0:
        taxable_idx = col_map.get('April 2026 Taxable Salary', -1)

    income_tax_idx = col_map.get('Income Tax', -1)
    if income_tax_idx < 0:
        income_tax_idx = col_map.get('April Income Tax', -1)

    if taxable_idx < 0 or income_tax_idx < 0:
        print(f'  Missing required columns\n')
        continue

    batch_requests = []
    entity_taxable = 0
    entity_tax = 0

    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if not emp_name:
            continue

        total_allow = row[total_allow_idx] if total_allow_idx >= 0 and total_allow_idx < len(row) else ''
        medical = row[medical_idx] if medical_idx >= 0 and medical_idx < len(row) else ''
        unpaid = row[unpaid_idx] if unpaid_idx >= 0 and unpaid_idx < len(row) else ''

        # Calculate Taxable Salary
        try:
            total_allow_num = float(str(total_allow).replace(',', '').strip()) if total_allow else 0
            medical_num = float(str(medical).replace(',', '').strip()) if medical else 0
            unpaid_num = float(str(unpaid).replace(',', '').strip()) if unpaid else 0

            taxable_salary = total_allow_num - medical_num - unpaid_num
        except:
            taxable_salary = 0

        # Get income tax from revised data
        emp_name_lower = emp_name.lower()
        income_tax = revised_tax_data.get(emp_name_lower, 0)

        # Add to batch
        taxable_col = chr(65 + taxable_idx) if taxable_idx < 26 else chr(64 + taxable_idx // 26) + chr(65 + taxable_idx % 26)
        tax_col = chr(65 + income_tax_idx) if income_tax_idx < 26 else chr(64 + income_tax_idx // 26) + chr(65 + income_tax_idx % 26)

        batch_requests.append({
            'range': f'{entity}!{taxable_col}{row_idx}',
            'values': [[taxable_salary]]
        })
        entity_taxable += 1

        batch_requests.append({
            'range': f'{entity}!{tax_col}{row_idx}',
            'values': [[income_tax]]
        })
        entity_tax += 1

        total_processed += 1

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=NEW_SHEET_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  Calculated Taxable Salary: {entity_taxable} employees')
        print(f'  Calculated Income Tax: {entity_tax} employees')
        total_taxable_calcs += entity_taxable
        total_income_tax_calcs += entity_tax

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print(f'Total Employees Processed: {total_processed}')
print(f'Taxable Salary Calculated: {total_taxable_calcs}')
print(f'Income Tax Calculated: {total_income_tax_calcs}')
print()
print('[COMPLETE] Taxable Salary and Income Tax calculations finished')
print()
