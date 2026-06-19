#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract 9-Month Tax History (Jul 2025 - Mar 2026)
Build database of employee tax deductions across financial year
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
print('EXTRACTING 9-MONTH TAX HISTORY (FY Jul 2025 - Jun 2026)')
print('=' * 120)
print()

# Payroll sheets to process
payroll_months = [
    ('July 2025', '1j9IYtxj38mUYPT8kOGOhuyOm7wtbiccaCjxJPTvlM24'),
    ('August 2025', '1FCiMTGim6EqWJRL7UVA3V31bH8KvICVs7a895pjoIuE'),
    ('September 2025', '1sLo1cv5tWqoj1Shtyp2eZjSW6UEz_z__VU8CnFDfW-A'),
    ('October 2025', '1nCuye_IqKEipyKNWvAz9pJ3LLwEpnR2z6raoPVfmGRY'),
    ('November 2025', '1NHnjvsJc-hk9l7qQvOTQr3znKFPzjc9mEBbtKWmJjjA'),
    ('December 2025', '1FprPYHx-S_RaV-C5HGGENg3BVeWzhmn3eUx1Ofuk7gk'),
    ('January 2026', '1EXJhbbqI952ick9-VhSX3k6MxC6oGSVeg9NJfrlYqeI'),
    ('February 2026', '1v-vLLvij1phN_havWvGzbOWaz1apQcs3unHAectyTdY'),
    ('March 2026', '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk')
]

# Database: employee_name -> {month -> {tax, gross_salary, etc}}
tax_database = {}

# Process each month
for month_idx, (month_name, sheet_id) in enumerate(payroll_months, 1):
    print(f'[{month_idx}/9] {month_name}')
    print('-' * 120)

    try:
        # Get sheet metadata to find entity tabs
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        entity_tabs = [s['properties']['title'] for s in metadata['sheets']
                      if 'NIETE' in s['properties']['title'] or s['properties']['title'] in ['OPL', 'OWT', 'Taleemabad_Inc_']]

        print(f'  Found {len(entity_tabs)} entity tabs: {", ".join(entity_tabs[:3])}{"..." if len(entity_tabs) > 3 else ""}')

        # Process each entity tab
        for entity_tab in entity_tabs:
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=f'{entity_tab}!A1:AA500'
                ).execute()

                values = result.get('values', [])
                if not values or len(values) < 2:
                    continue

                headers = values[0]

                # Find column indices
                col_map = {h: i for i, h in enumerate(headers)}
                name_idx = col_map.get('Employee Name', -1)
                tax_idx = col_map.get('Income Tax', -1)
                gross_idx = col_map.get('Gross Salary', -1)

                if name_idx < 0 or tax_idx < 0:
                    continue

                # Extract data for each employee
                for row in values[1:]:
                    if len(row) > name_idx and row[name_idx]:
                        emp_name = str(row[name_idx]).strip()
                        emp_name_lower = emp_name.lower()

                        tax_val = row[tax_idx] if tax_idx < len(row) else ''
                        gross_val = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''

                        # Parse tax value
                        try:
                            tax_amount = float(str(tax_val).replace(',', '').strip() or 0)
                        except:
                            tax_amount = 0

                        # Parse gross salary
                        try:
                            gross_amount = float(str(gross_val).replace(',', '').strip() or 0)
                        except:
                            gross_amount = 0

                        # Add to database
                        if emp_name_lower not in tax_database:
                            tax_database[emp_name_lower] = {}

                        tax_database[emp_name_lower][month_name] = {
                            'name': emp_name,
                            'entity': entity_tab,
                            'tax': tax_amount,
                            'gross': gross_amount
                        }

            except Exception as e:
                continue

        print(f'  Extracted data from {len(entity_tabs)} entities')
        print()

    except Exception as e:
        print(f'  ERROR: {str(e)[:60]}...')
        print()

print('=' * 120)
print('EXTRACTION COMPLETE')
print('=' * 120)
print()

print(f'Total unique employees found: {len(tax_database)}')
print()

# Show sample data
print('Sample: First 5 employees and their 9-month tax history:')
print('-' * 120)

for emp_idx, (name_lower, months_data) in enumerate(list(tax_database.items())[:5], 1):
    emp_name = months_data.get(list(months_data.keys())[0], {}).get('name', name_lower) if months_data else name_lower
    emp_name_clean = emp_name.encode('utf-8', errors='ignore').decode('utf-8')

    print(f'\n{emp_idx}. {emp_name_clean}')

    total_tax = 0
    for month_name, month_data in sorted(months_data.items()):
        tax = month_data.get('tax', 0)
        total_tax += tax
        print(f'   {month_name:20} Tax: {tax:8.0f}  Gross: {month_data.get("gross", 0):10.0f}')

    print(f'   {"TOTAL (9 months)":20} Tax: {total_tax:8.0f}')

print()
print('=' * 120)
print('NEXT: Calculate annual projections and remaining tax for Apr-May-Jun 2026')
print('=' * 120)

# Save to file for reference
with open('tax_history_9months.json', 'w') as f:
    json.dump(tax_database, f, indent=2)

print()
print('Tax database saved to: tax_history_9months.json')
