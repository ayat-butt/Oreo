#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEBUG: Check what values are in April column of tax sheet
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

TAX_SHEET_ID = '1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs'

# Load tax sheet
result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range='TAX DEDUCTION DETAILS!A1:M500'
).execute()

values = result.get('values', [])
headers = values[0]

print('Tax sheet headers:')
for i, h in enumerate(headers):
    print(f'  Column {i} ({chr(65 + i)}): {h}')

print()

# Find April column
april_idx = -1
for i, h in enumerate(headers):
    if 'apr' in str(h).lower():
        april_idx = i
        print(f'April column: Index {i} = {h}')
        break

print()
print('Sample data (first 15 employees, April column):')
print('-' * 80)

for i, row in enumerate(values[1:16], 1):
    name = row[1] if len(row) > 1 else ''
    april_val = row[april_idx] if april_idx >= 0 and april_idx < len(row) else ''

    print(f'  {i:2}. {name:30} → April: "{april_val}"')

print()
print('Checking how many have April values:')
with_april = 0
without_april = 0

for row in values[1:]:
    if len(row) > 1 and row[1]:
        april_val = row[april_idx] if april_idx >= 0 and april_idx < len(row) else ''
        if april_val and str(april_val).strip():
            with_april += 1
        else:
            without_april += 1

print(f'  With April tax: {with_april}')
print(f'  Without April tax: {without_april}')
