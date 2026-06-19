#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check OPL columns in both sheets
"""

import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('../token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

REVISED_SHEET_ID = '1OUR1Bj9aqF1JekArcfqmlE3nP9kBHqMfJZWJuo3kK8E'
AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 120)
print('REVISED APRIL 2026 - OPL SHEET COLUMNS')
print('=' * 120)
print()

result = service.spreadsheets().values().get(
    spreadsheetId=REVISED_SHEET_ID,
    range='OPL!A1:AI1'
).execute()

values = result.get('values', [])
if values:
    headers = values[0]
    for idx, h in enumerate(headers):
        col_letter = chr(65 + idx) if idx < 26 else chr(64 + idx // 26) + chr(65 + idx % 26)
        print(f'{col_letter:3s} ({idx:2d}): {h}')

print()
print('=' * 120)
print('AGENT PAYROLL - OPL SHEET COLUMNS')
print('=' * 120)
print()

result = service.spreadsheets().values().get(
    spreadsheetId=AGENT_PAYROLL_ID,
    range='OPL!A1:AI1'
).execute()

values = result.get('values', [])
if values:
    headers = values[0]
    for idx, h in enumerate(headers):
        col_letter = chr(65 + idx) if idx < 26 else chr(64 + idx // 26) + chr(65 + idx % 26)
        print(f'{col_letter:3s} ({idx:2d}): {h}')
