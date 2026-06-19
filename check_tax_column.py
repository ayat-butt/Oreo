#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check April tax column values"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

TAX_SHEET_ID = '1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs'

result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range='TAX DEDUCTION DETAILS!A1:M50'
).execute()

values = result.get('values', [])

print('First 20 rows, April column (M):')
print()

for i, row in enumerate(values[:21], 1):
    if len(row) > 1:
        name = row[1] if row[1] else ''
        april = row[12] if len(row) > 12 else ''

        clean_name = str(name).encode('utf-8', errors='ignore').decode('utf-8')
        print(f'Row {i:2}: {clean_name:30} = {april}')

print()

# Count non-empty April values
non_empty = sum(1 for row in values[1:] if len(row) > 12 and row[12] and str(row[12]).strip())
print(f'Total rows with April tax value: {non_empty}')
