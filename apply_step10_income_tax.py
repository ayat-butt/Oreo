#!/usr/bin/env python3
"""
STEP 10: Apply Income Tax (LOOKUP-based from TAX DEDUCTION DETAILS sheet)
For ALL 185 employees - no exclusions
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load token
with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
TAX_SHEET_ID = '1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs'

print('=' * 80)
print('STEP 10: APPLYING INCOME TAX (LOOKUP-BASED)')
print('=' * 80)
print()

# Step 1: Fetch TAX DEDUCTION DETAILS sheet
print('Fetching TAX DEDUCTION DETAILS sheet...')

metadata = service.spreadsheets().get(spreadsheetId=TAX_SHEET_ID).execute()
sheets = [sheet['properties']['title'] for sheet in metadata['sheets']]

print(f'Available tabs: {sheets[:10]}')
print()

# Get all data from the main tab (usually first tab with tax data)
result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range='TAX DEDUCTION DETAILS!A1:L500'
).execute()

values = result.get('values', [])

if not values:
    print('Trying alternate tab name...')
    result = service.spreadsheets().values().get(
        spreadsheetId=TAX_SHEET_ID,
        range='Sheet1!A1:L500'
    ).execute()
    values = result.get('values', [])

# Parse header to find APRIL column
print(f'Total rows fetched: {len(values)}')

header = values[0] if values else []
april_col_idx = None

print(f'Header row: {header}')
print()

for idx, col_name in enumerate(header):
    if col_name and 'APR' in str(col_name).upper():
        april_col_idx = idx
        print(f'Found APRIL column at index {idx}: {col_name}')
        break

if april_col_idx is None:
    print('ERROR: APRIL column not found in header')
    print('Searching for alternative column names...')
    for idx, col_name in enumerate(header):
        print(f'  [{idx}] {col_name}')
    exit(1)

print()

# Extract tax data for April
print('Extracting tax data for April...')

tax_data = {}

for row_idx, row in enumerate(values[1:], start=2):
    if len(row) > april_col_idx:
        emp_name = str(row[0]).strip() if row else ''
        tax_value = row[april_col_idx] if april_col_idx < len(row) else ''

        if emp_name and emp_name != 'Name':
            try:
                if tax_value:
                    tax_val = float(str(tax_value).replace(',', '').replace('(', '').replace(')', ''))
                    # Handle negative (parentheses) as negative values
                    if '(' in str(tax_value):
                        tax_val = -tax_val
                else:
                    tax_val = 0

                tax_data[emp_name] = tax_val
            except:
                tax_data[emp_name] = 0

print(f'Extracted tax data for {len(tax_data)} employees')
print()

# Apply to payroll sheet
print('Applying tax data to payroll sheet...')
print()

payroll_metadata = service.spreadsheets().get(spreadsheetId=PAYROLL_SHEET_ID).execute()
payroll_sheets = [sheet['properties']['title'] for sheet in payroll_metadata['sheets']]

applied = 0
not_found_list = []
found_employees = set()

for entity in payroll_sheets:
    if entity.startswith('NIETE') or entity in ['OPL', 'OWT', 'Taleemabad_Inc_']:
        result = service.spreadsheets().values().get(
            spreadsheetId=PAYROLL_SHEET_ID,
            range=f'{entity}!A1:S500'
        ).execute()

        values = result.get('values', [])

        for row_idx, row in enumerate(values):
            if row_idx == 0:
                continue  # Skip header
            if len(row) < 2:
                continue

            emp_name = str(row[1]).strip() if len(row) > 1 else ''

            # Try exact match first, then case-insensitive
            tax_val = None

            for tax_name, tax_amount in tax_data.items():
                if tax_name.lower() == emp_name.lower():
                    tax_val = tax_amount
                    found_employees.add(emp_name)
                    break

            if tax_val is not None:
                # Column R = Income Tax (column 17, 0-indexed = 17)
                service.spreadsheets().values().update(
                    spreadsheetId=PAYROLL_SHEET_ID,
                    range=f'{entity}!R{row_idx + 1}',
                    valueInputOption='RAW',
                    body={'values': [[tax_val]]}
                ).execute()
                applied += 1

                if tax_val != 0:
                    print(f'Applied PKR {tax_val:,.2f} to {emp_name} ({entity})')

print()
print('=' * 80)
print('STEP 10 COMPLETE: INCOME TAX APPLIED')
print('=' * 80)
print()
print(f'Total Applied: {applied} employees')
print(f'Total Tax Records Available: {len(tax_data)} employees')
print(f'Employees Not Found in Payroll: {len(tax_data) - len(found_employees)}')
