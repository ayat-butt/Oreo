#!/usr/bin/env python3
"""
Fetch data for:
STEP 3: Commute Allowance (NIETE ICT CPD COACHES only)
STEP 4: Meal Deductions (NIETE ICT employees, 5,720 fixed)
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load token
with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

print('=' * 80)
print('STEP 3 & 4: COMMUTE ALLOWANCE & MEAL DEDUCTIONS')
print('=' * 80)
print()

# STEP 3: Commute Allowance
print('STEP 3: COMMUTE ALLOWANCE - NIETE ICT CPD COACHES')
print('-' * 80)

COMMUTE_SHEET_ID = '10kM4xcC0S7nSJhU5HfH6ZdbiTxqyzw5P4_z5nOJ7lck'

# Get sheet metadata to find April 2026 tab
metadata = service.spreadsheets().get(spreadsheetId=COMMUTE_SHEET_ID).execute()
sheets = metadata.get('sheets', [])

april_tab = None
for sheet in sheets:
    if 'April 2026' in sheet['properties']['title'] or 'april' in sheet['properties']['title'].lower():
        april_tab = sheet['properties']['title']
        break

if april_tab:
    print(f'Found tab: {april_tab}')
    result = service.spreadsheets().values().get(
        spreadsheetId=COMMUTE_SHEET_ID,
        range=f'{april_tab}!A1:B100'
    ).execute()

    values = result.get('values', [])

    print()
    print('CPD COACHES with Commute Allowance for April 2026:')
    print()

    commute_data = {}
    for row in values[1:]:  # Skip header
        if row and len(row) >= 2:
            name = str(row[0]).strip()
            amount = row[1]
            if name and amount:
                try:
                    amount_val = float(str(amount).replace(',', '')) if amount else 0
                    commute_data[name] = amount_val
                    print(f'  {name}: PKR {amount_val:,.0f}')
                except:
                    pass

    print(f'\nTotal CPD Coaches with commute: {len(commute_data)}')
else:
    print('April 2026 tab not found in Commute Allowance sheet')

print()
print()

# STEP 4: Meal Deductions
print('STEP 4: MEAL DEDUCTIONS - NIETE ICT EMPLOYEES')
print('-' * 80)

MEAL_SHEET_ID = '1iZMCJe6aHxxwVsCKpIqzu4g4ZAvYci76noOeSB2byD4'

# Get sheet metadata to find April 2026 tab
metadata = service.spreadsheets().get(spreadsheetId=MEAL_SHEET_ID).execute()
sheets = metadata.get('sheets', [])

april_tab = None
for sheet in sheets:
    if 'April 2026' in sheet['properties']['title'] or 'april' in sheet['properties']['title'].lower():
        april_tab = sheet['properties']['title']
        break

if april_tab:
    print(f'Found tab: {april_tab}')
    result = service.spreadsheets().values().get(
        spreadsheetId=MEAL_SHEET_ID,
        range=f'{april_tab}!A1:A200'
    ).execute()

    values = result.get('values', [])

    print()
    print('NIETE ICT Employees with Meal Deduction (5,720) for April 2026:')
    print()

    meal_deduction_amount = 5720
    meal_data = {}

    for row in values[1:]:  # Skip header
        if row and row[0]:
            name = str(row[0]).strip()
            if name:
                meal_data[name] = meal_deduction_amount
                print(f'  {name}: PKR {meal_deduction_amount:,.0f}')

    print(f'\nTotal NIETE ICT employees with meal deduction: {len(meal_data)}')
else:
    print('April 2026 tab not found in Meal Deduction sheet')

print()
print('=' * 80)
print('STEP 3 & 4 DATA FETCHED')
print('=' * 80)
