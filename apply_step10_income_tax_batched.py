#!/usr/bin/env python3
"""
STEP 10: Apply Income Tax (BATCHED for efficiency)
For ALL 185 employees - uses batch update to avoid rate limits
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
print('STEP 10: INCOME TAX - BATCHED UPDATE')
print('=' * 80)
print()

# Fetch tax data
print('Fetching tax data...')

result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range='TAX DEDUCTION DETAILS!A1:M500'
).execute()

tax_values = result.get('values', [])

tax_data = {}

for row in tax_values[1:]:
    if len(row) > 1:
        emp_name = str(row[1]).strip() if row[1] else ''
        tax_val = row[12] if len(row) > 12 else ''

        if emp_name:
            try:
                if tax_val and str(tax_val).strip():
                    val = float(str(tax_val).replace(',', '').replace('(', '').replace(')', ''))
                    if '(' in str(tax_val):
                        val = -val
                    tax_data[emp_name] = val
                else:
                    tax_data[emp_name] = 0
            except:
                tax_data[emp_name] = 0

print(f'Extracted tax for {len(tax_data)} employees')
print()

# Get payroll data and prepare batch requests
print('Preparing batch updates...')

payroll_metadata = service.spreadsheets().get(spreadsheetId=PAYROLL_SHEET_ID).execute()
payroll_sheets = [sheet['properties']['title'] for sheet in payroll_metadata['sheets']]

batch_requests = []
applied = 0

for entity in payroll_sheets:
    if entity in ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']:
        result = service.spreadsheets().values().get(
            spreadsheetId=PAYROLL_SHEET_ID,
            range=f'{entity}!A1:S500'
        ).execute()

        payroll_rows = result.get('values', [])

        for row_idx, row in enumerate(payroll_rows):
            if row_idx == 0 or len(row) < 2:
                continue

            emp_name = str(row[1]).strip()

            # Find matching tax entry
            for tax_name, tax_amount in tax_data.items():
                if tax_name.lower() == emp_name.lower():
                    batch_requests.append({
                        'range': f'{entity}!R{row_idx + 1}',
                        'values': [[tax_amount]]
                    })
                    applied += 1
                    break

print(f'Prepared {len(batch_requests)} batch requests')
print()

# Execute batch update
print('Executing batch update...')

if batch_requests:
    body = {
        'data': batch_requests,
        'valueInputOption': 'RAW'
    }

    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=PAYROLL_SHEET_ID,
        body=body
    ).execute()

    total_updated = result.get('totalUpdatedCells', 0)

    print()
    print('=' * 80)
    print('STEP 10 COMPLETE')
    print('=' * 80)
    print()
    print(f'Total Cells Updated: {total_updated}')
    print(f'Employees Processed: {applied}')
    print(f'Income Tax Applied: YES')
else:
    print('No matching employees found!')
