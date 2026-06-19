#!/usr/bin/env python3
"""
STEP 10: Apply Income Tax - SLOW (entity-by-entity, with delays)
Avoids rate limiting by processing one entity at a time
"""

import json
import time
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
print('STEP 10: INCOME TAX - ENTITY-BY-ENTITY UPDATE')
print('=' * 80)
print()

# Fetch tax data once
print('Fetching tax reference data...')

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

print(f'Tax data loaded for {len(tax_data)} employees')
print()

# Get payroll sheets
payroll_metadata = service.spreadsheets().get(spreadsheetId=PAYROLL_SHEET_ID).execute()
entities = [sheet['properties']['title'] for sheet in payroll_metadata['sheets']]

total_applied = 0

# Process each entity separately
for entity in ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']:
    if entity not in entities:
        continue

    print(f'Processing {entity}...')

    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:S500'
    ).execute()

    payroll_rows = result.get('values', [])

    # Build batch for this entity
    batch_requests = []

    for row_idx, row in enumerate(payroll_rows):
        if row_idx == 0 or len(row) < 2:
            continue

        emp_name = str(row[1]).strip()

        # Find tax value
        for tax_name, tax_amount in tax_data.items():
            if tax_name.lower() == emp_name.lower():
                batch_requests.append({
                    'range': f'{entity}!R{row_idx + 1}',
                    'values': [[tax_amount]]
                })
                total_applied += 1
                break

    # Execute batch for this entity
    if batch_requests:
        print(f'  Updating {len(batch_requests)} employees...')

        body = {
            'data': batch_requests,
            'valueInputOption': 'RAW'
        }

        try:
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=PAYROLL_SHEET_ID,
                body=body
            ).execute()

            updated = result.get('totalUpdatedCells', 0)
            print(f'  Cells updated: {updated}')
        except Exception as e:
            print(f'  ERROR: {e}')

    # Wait between entities to avoid rate limit
    print(f'  Waiting 2 seconds...')
    time.sleep(2)

print()
print('=' * 80)
print('STEP 10 COMPLETE')
print('=' * 80)
print()
print(f'Total Income Tax entries applied: {total_applied}')
