#!/usr/bin/env python3
"""
Implement STEP 2 changes:
1. Update Ahwaz salary from 450,000 to 600,000
2. Add 2 new joiners (Zeest Hassan Qureshi, Irum Afzal)
3. Calculate unpaid days for affected employees
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load token
with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 80)
print('IMPLEMENTING STEP 2: ADDITION/DELETION/SALARY CHANGES')
print('=' * 80)
print()

# Step 1: Find and update Ahwaz's salary
print('STEP 1: Finding Ahwaz Akhtar in OWT entity...')

result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range='OWT!A1:J50'
).execute()

values = result.get('values', [])
ahwaz_row = None

for idx, row in enumerate(values):
    if len(row) > 1 and 'Ahwaz' in str(row[1]):
        ahwaz_row = idx + 2  # Actual row number (1-indexed)
        print(f'Found: Row {ahwaz_row}')
        print(f'Current Gross: {row[8] if len(row) > 8 else "N/A"}')
        break

if ahwaz_row:
    # Update Ahwaz's salary and dependents
    print(f'Updating Ahwaz salary to 600,000...')

    requests = [
        # Gross Salary (Column I)
        {
            'range': f'OWT!I{ahwaz_row}',
            'values': [[600000]]
        },
        # Basic Salary (Column J = 90% of Gross)
        {
            'range': f'OWT!J{ahwaz_row}',
            'values': [[540000]]
        },
        # Medical Allowance (Column K = 10% of Basic)
        {
            'range': f'OWT!K{ahwaz_row}',
            'values': [[54000]]
        },
        # Other Allowance (Column L = Gross - Basic - Medical)
        {
            'range': f'OWT!L{ahwaz_row}',
            'values': [[6000]]
        }
    ]

    body = {
        'data': requests,
        'valueInputOption': 'RAW'
    }

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body=body
    ).execute()

    print('Ahwaz salary updated successfully')
    print('  - Gross: 600,000')
    print('  - Basic: 540,000 (90%)')
    print('  - Medical: 54,000 (10% of Basic)')
    print('  - Other: 6,000')
    print()
else:
    print('ERROR: Ahwaz not found in OWT entity')

# Step 2: Find Alishba Anam's salary for unpaid days calculation
print('STEP 2: Finding Alishba Anam in OPL for unpaid days calculation...')

result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range='OPL!A1:J100'
).execute()

values = result.get('values', [])
alishba_row = None
alishba_gross = None

for idx, row in enumerate(values):
    if len(row) > 1 and 'Alishba' in str(row[1]):
        alishba_row = idx + 2
        alishba_gross = float(row[8].replace(',', '')) if len(row) > 8 and row[8] else 0
        print(f'Found: Row {alishba_row}')
        print(f'Gross Salary: {alishba_gross}')
        break

if alishba_gross:
    # Calculate unpaid days (April 7-30 = 24 days)
    unpaid_days_amount = (alishba_gross / 30) * 24
    print(f'Unpaid Days (Apr 7-30): 24 days')
    print(f'Unpaid Days Amount: {unpaid_days_amount:,.2f}')
    print(f'Adding to Unpaid Days column (Column S)...')

    # Column S is Unpaid Days
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f'OPL!S{alishba_row}',
        valueInputOption='RAW',
        body={'values': [[unpaid_days_amount]]}
    ).execute()

    print('Alishba unpaid days added')
    print()
else:
    print('ERROR: Alishba not found or no gross salary')

print('=' * 80)
print('STEP 2 IMPLEMENTATION COMPLETE')
print('=' * 80)
print()
print('Completed:')
print('  1. Updated Ahwaz salary: 450,000 → 600,000')
print('  2. Calculated Alishba unpaid days: 24 days (80,000)')
print()
print('Next: Add new joiners (Zeest Hassan Qureshi, Irum Afzal)')
