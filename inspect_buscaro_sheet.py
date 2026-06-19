#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inspect BusCaro sheet structure to understand the data layout
"""

import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

BUSCARO_SHEET_ID = '12EyDg8UAuDFexpJ_oC7hCN2HU0lDuQbAHHkmbdFKJwQ'

print('=' * 100)
print('INSPECTING BusCARO SHEET STRUCTURE')
print('=' * 100)
print()

# Get metadata about the sheet
metadata = service.spreadsheets().get(spreadsheetId=BUSCARO_SHEET_ID).execute()

print('Available tabs:')
for sheet in metadata['sheets']:
    print(f'  - {sheet["properties"]["title"]}')

print()
print('=' * 100)
print('LOADING APRIL 2026 TAB')
print('=' * 100)
print()

# Load April 2026 tab
result = service.spreadsheets().values().get(
    spreadsheetId=BUSCARO_SHEET_ID,
    range='April 2026!A1:G100'
).execute()

values = result.get('values', [])

if values:
    print(f'Headers (Row 1): {values[0]}')
    print()
    print('Sample rows (first 10):')
    print()

    for i, row in enumerate(values[1:11], 2):
        print(f'Row {i}: {row}')
    print()

    if len(values) > 11:
        print(f'... Total {len(values)} rows ...')
else:
    print('No data found')
