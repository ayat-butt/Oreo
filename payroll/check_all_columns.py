#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check all columns in Agent sheet
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

AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('AGENT PAYROLL SHEET - ALL COLUMNS')
print()

result = service.spreadsheets().values().get(
    spreadsheetId=AGENT_PAYROLL_ID,
    range='NIETE_Islamabad!A1:AZ1'
).execute()

values = result.get('values', [])
if values:
    headers = values[0]
    for idx, h in enumerate(headers):
        col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
        print(f'{col_letter:3s} ({idx:2d}): {h}')
