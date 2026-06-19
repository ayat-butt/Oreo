#!/usr/bin/env python3
"""
Add 2 new joiners:
1. Zeest Hassan Qureshi (OPL) - Joining April 7, Salary 400,000
2. Irum Afzal (NIETE_Islamabad) - Joining April 20, Salary 119,000
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
print('ADDING NEW JOINERS')
print('=' * 80)
print()

# Get sheet structure to find last rows
metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
sheets_info = {sheet['properties']['title']: sheet for sheet in metadata['sheets']}

# Step 1: Add Zeest Hassan Qureshi to OPL
print('STEP 1: Adding Zeest Hassan Qureshi to OPL...')
print('Entity: OPL')
print('Joining Date: April 7, 2026')
print('Gross Salary: 400,000')
print()

# Zeest data
zeest_data = [
    ['', 'Zeest Hassan Qureshi', 'Senior Manager - Growth', 'Growth', '', '', '', '', 400000, 360000, 36000, 4000, 0, 0, 0, 114400]
    # Columns: A-R (Employee ID, Name, Title, Dept, CNIC, JoinDate, Bank, Account, Gross, Basic, Medical, Other, Overtime, Commute, PendingDues, UnpaidDays)
]

# Find last row in OPL and add new row
opl_result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range='OPL!A:A'
).execute()
opl_values = opl_result.get('values', [])
opl_last_row = len(opl_values) + 1

print(f'Adding at OPL row {opl_last_row}')

service.spreadsheets().values().append(
    spreadsheetId=SHEET_ID,
    range=f'OPL!A{opl_last_row}',
    valueInputOption='RAW',
    body={'values': zeest_data}
).execute()

print('Zeest Hassan Qureshi added successfully')
print()

# Step 2: Add Irum Afzal to NIETE_Islamabad
print('STEP 2: Adding Irum Afzal to NIETE_Islamabad...')
print('Entity: NIETE_Islamabad')
print('Joining Date: April 20, 2026')
print('Gross Salary: 119,000')
print()

# Irum data with unpaid days: 19 days = (119,000 / 30) * 19 = 75,366.67
irum_unpaid_amount = (119000 / 30) * 19

irum_data = [
    ['', 'Irum Afzal', 'CPD Coach', '', '', '', '', '', 119000, 107100, 10710, 1190, 0, 0, 0, irum_unpaid_amount]
    # Columns: A-R
]

# Find last row in NIETE_Islamabad and add new row
niete_result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID,
    range='NIETE_Islamabad!A:A'
).execute()
niete_values = niete_result.get('values', [])
niete_last_row = len(niete_values) + 1

print(f'Adding at NIETE_Islamabad row {niete_last_row}')

service.spreadsheets().values().append(
    spreadsheetId=SHEET_ID,
    range=f'NIETE_Islamabad!A{niete_last_row}',
    valueInputOption='RAW',
    body={'values': irum_data}
).execute()

print('Irum Afzal added successfully')
print(f'Unpaid Days: 19 days = PKR {irum_unpaid_amount:,.2f}')
print()

print('=' * 80)
print('NEW JOINERS ADDED SUCCESSFULLY')
print('=' * 80)
print()
print('Summary:')
print('1. Zeest Hassan Qureshi - OPL - 400,000 - Unpaid: 6 days (80,000)')
print('2. Irum Afzal - NIETE_Islamabad - 119,000 - Unpaid: 19 days (75,367)')
