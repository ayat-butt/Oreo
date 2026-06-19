#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Track Abdul Waheed across all payroll sheets and entities
Find salary changes and entity transfers
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

# Known payroll sheet IDs from context
print('=' * 120)
print('TRACKING ABDUL WAHEED ACROSS ALL PAYROLL SHEETS')
print('=' * 120)
print()

# We have March 2026 and April 2026 sheets - need July 2025 to Feb 2026
# Let me search for Abdul Waheed in the known sheets first

MARCH_SHEET_ID = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
APRIL_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

# Track Abdul Waheed
abdul_history = {}

print('MARCH 2026 (Current Entity):')
print()

result = service.spreadsheets().values().get(
    spreadsheetId=MARCH_SHEET_ID,
    range=f'NIETE_Islamabad!A1:AI500'
).execute()

values = result.get('values', [])
if values:
    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    gross_idx = col_map.get('Gross Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)
    ytd_idx = col_map.get('YTD Taxable (Jul–Feb)', -1)
    annual_tax_idx = col_map.get('Annual Tax Liability (FBR)', -1)
    tax_collected_idx = col_map.get('Tax Collected So Far (Jul–Feb)', -1)

    for row in values[1:]:
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if 'Abdul Waheed' not in emp_name and emp_name:
            continue

        if 'Abdul Waheed' in emp_name:
            gross = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
            income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''
            ytd = row[ytd_idx] if ytd_idx >= 0 and ytd_idx < len(row) else ''
            annual_tax = row[annual_tax_idx] if annual_tax_idx >= 0 and annual_tax_idx < len(row) else ''
            tax_collected = row[tax_collected_idx] if tax_collected_idx >= 0 and tax_collected_idx < len(row) else ''

            print(f'Found in NIETE_Islamabad:')
            print(f'  Gross Salary: {gross}')
            print(f'  Income Tax (March): {income_tax}')
            print(f'  YTD Taxable: {ytd}')
            print(f'  Annual Tax Liability: {annual_tax}')
            print(f'  Tax Collected So Far: {tax_collected}')
            print()

            abdul_history['NIETE_Islamabad_March'] = {
                'gross': gross,
                'income_tax': income_tax,
                'ytd': ytd,
                'annual_tax': annual_tax,
                'tax_collected': tax_collected
            }

print()
print('APRIL 2026 (Current Entity):')
print()

result = service.spreadsheets().values().get(
    spreadsheetId=APRIL_SHEET_ID,
    range=f'NIETE_Islamabad!A1:AI500'
).execute()

values = result.get('values', [])
if values:
    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    gross_idx = col_map.get('Gross Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)
    ytd_idx = col_map.get('YTD Taxable (Jul–Feb)', -1)
    annual_tax_idx = col_map.get('Annual Tax Liability (FBR)', -1)
    tax_collected_idx = col_map.get('Tax Collected So Far (Jul–Feb)', -1)

    for row in values[1:]:
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if 'Abdul Waheed' not in emp_name and emp_name:
            continue

        if 'Abdul Waheed' in emp_name:
            gross = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
            income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''
            ytd = row[ytd_idx] if ytd_idx >= 0 and ytd_idx < len(row) else ''
            annual_tax = row[annual_tax_idx] if annual_tax_idx >= 0 and annual_tax_idx < len(row) else ''
            tax_collected = row[tax_collected_idx] if tax_collected_idx >= 0 and tax_collected_idx < len(row) else ''

            print(f'Found in NIETE_Islamabad:')
            print(f'  Gross Salary: {gross}')
            print(f'  Income Tax (April): {income_tax}')
            print(f'  YTD Taxable: {ytd}')
            print(f'  Annual Tax Liability: {annual_tax}')
            print(f'  Tax Collected So Far: {tax_collected}')
            print()

            abdul_history['NIETE_Islamabad_April'] = {
                'gross': gross,
                'income_tax': income_tax,
                'ytd': ytd,
                'annual_tax': annual_tax,
                'tax_collected': tax_collected
            }

print()
print('SEARCHING OTHER ENTITIES FOR ABDUL WAHEED:')
print()

# Search all other entities in both sheets
for entity in ['OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']:
    print(f'{entity}:')

    result_march = service.spreadsheets().values().get(
        spreadsheetId=MARCH_SHEET_ID,
        range=f'{entity}!A1:R500'
    ).execute()

    result_april = service.spreadsheets().values().get(
        spreadsheetId=APRIL_SHEET_ID,
        range=f'{entity}!A1:R500'
    ).execute()

    found_march = False
    found_april = False

    for result, sheet_name in [(result_march, 'March'), (result_april, 'April')]:
        values = result.get('values', [])
        if values:
            headers = values[0]
            col_map = {h.strip(): i for i, h in enumerate(headers)}
            name_idx = col_map.get('Employee Name', 1)
            gross_idx = col_map.get('Gross Salary', -1)
            income_tax_idx = col_map.get('Income Tax', -1)

            for row in values[1:]:
                emp_name = row[name_idx] if name_idx < len(row) else ''
                if 'Abdul Waheed' in emp_name:
                    gross = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
                    income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''

                    print(f'  ✓ FOUND in {entity} ({sheet_name})')
                    print(f'    Gross: {gross}, Tax: {income_tax}')

                    if sheet_name == 'March':
                        found_march = True
                    else:
                        found_april = True

    if not found_march and not found_april:
        print(f'  Not found')

    print()

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print('Abdul Waheed History:')
for key, value in abdul_history.items():
    print(f'{key}:')
    print(f'  Gross: {value["gross"]}, Tax: {value["income_tax"]}')
    print(f'  YTD: {value["ytd"]}, Collected: {value["tax_collected"]}')
    print()

print('Check the history to see:')
print('1. If salary changed')
print('2. If he moved between entities')
print('3. Why YTD Taxable and Tax Collected are blank in April')
