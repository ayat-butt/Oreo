#!/usr/bin/env python3
"""
Apply STEP 3 & 4 to payroll:
- STEP 3: Add Commute Allowance for CPD COACHES (35 entries)
- STEP 4: Add Meal Deductions 5,720 for NIETE ICT employees (18 entries)
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

print('=' * 80)
print('STEP 3 & 4: APPLYING COMMUTE & MEAL DEDUCTIONS')
print('=' * 80)
print()

# Step 3: Fetch commute allowance data
print('STEP 3: Fetching Commute Allowance data...')

commute_result = service.spreadsheets().values().get(
    spreadsheetId='10kM4xcC0S7nSJhU5HfH6ZdbiTxqyzw5P4_z5nOJ7lck',
    range='Apr-2026!A1:D100'
).execute()

commute_values = commute_result.get('values', [])
commute_data = {}

for row in commute_values[1:]:  # Skip header
    if row and len(row) >= 4:
        name = str(row[2]).strip()
        amount = str(row[3]).replace(',', '')
        try:
            amount_val = float(amount)
            commute_data[name] = amount_val
        except:
            pass

print(f'Found {len(commute_data)} CPD Coaches with commute allowance')
print()

# Step 4: Fetch meal deduction data
print('STEP 4: Fetching Meal Deduction data...')

meal_result = service.spreadsheets().values().get(
    spreadsheetId='1iZMCJe6aHxxwVsCKpIqzu4g4ZAvYci76noOeSB2byD4',
    range='April-2026!A2:A100'
).execute()

meal_values = meal_result.get('values', [])
meal_data = {}
meal_amount = 5720

for row in meal_values:
    if row and row[0]:
        name = str(row[0]).strip()
        meal_data[name] = meal_amount

print(f'Found {len(meal_data)} NIETE ICT employees with meal deduction')
print()

# Now apply to payroll sheet
print('Applying data to payroll sheet...')
print()

# Get payroll data for all entities
metadata = service.spreadsheets().get(spreadsheetId=PAYROLL_SHEET_ID).execute()
sheets = [sheet['properties']['title'] for sheet in metadata['sheets']]

applied_commute = 0
applied_meals = 0

# For each entity, find and update matching employees
for entity in sheets:
    if entity.startswith('NIETE') or entity == 'OPL' or entity == 'OWT' or entity == 'Taleemabad_Inc_':
        result = service.spreadsheets().values().get(
            spreadsheetId=PAYROLL_SHEET_ID,
            range=f'{entity}!A1:M500'
        ).execute()

        values = result.get('values', [])

        # Column M = Commute Allowance (column 13), Column S = Lunch Meal (column 19)
        # But we need to find the exact columns - let me use row 1 as header

        for row_idx, row in enumerate(values):
            if row_idx == 0:
                continue  # Skip header

            if len(row) < 2:
                continue

            emp_name = str(row[1]).strip() if len(row) > 1 else ''

            # Check commute
            if emp_name in commute_data:
                # Column M (12) = Commute Allowance
                update_range = f'{entity}!M{row_idx + 1}'
                service.spreadsheets().values().update(
                    spreadsheetId=PAYROLL_SHEET_ID,
                    range=update_range,
                    valueInputOption='RAW',
                    body={'values': [[commute_data[emp_name]]]}
                ).execute()
                applied_commute += 1

            # Check meal (column S = 18)
            if emp_name in meal_data:
                update_range = f'{entity}!S{row_idx + 1}'
                service.spreadsheets().values().update(
                    spreadsheetId=PAYROLL_SHEET_ID,
                    range=update_range,
                    valueInputOption='RAW',
                    body={'values': [[meal_data[emp_name]]]}
                ).execute()
                applied_meals += 1

print(f'Applied Commute Allowance: {applied_commute} entries')
print(f'Applied Meal Deductions: {applied_meals} entries')
print()

print('=' * 80)
print('STEP 3 & 4 COMPLETE')
print('=' * 80)
