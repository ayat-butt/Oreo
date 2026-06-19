#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Total Allowance formula in Agent sheet
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

print('=' * 120)
print('CHECKING TOTAL ALLOWANCE FORMULA IN AGENT SHEET')
print('=' * 120)
print()

for entity in ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']:
    print(f'{entity}:')

    # Get the first data row to check the formula
    result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:P3'
    ).execute()

    values = result.get('values', [])
    if values:
        headers = values[0]
        col_map = {h.strip(): i for i, h in enumerate(headers)}

        total_allow_idx = col_map.get('Total Allowance', -1)

        if total_allow_idx >= 0:
            col_letter = chr(65 + total_allow_idx) if total_allow_idx < 26 else chr(64 + total_allow_idx // 26) + chr(65 + total_allow_idx % 26)

            # Get formula from row 2
            result_formula = service.spreadsheets().get(
                spreadsheetId=AGENT_PAYROLL_ID,
                ranges=[f'{entity}!{col_letter}2'],
                includeGridData=True
            ).execute()

            grid_data = result_formula.get('sheets', [{}])[0].get('data', [{}])[0]
            row_data = grid_data.get('rowData', [{}])[0]
            cell = row_data.get('values', [{}])[0] if row_data.get('values') else {}

            formula = cell.get('userEnteredValue', {}).get('formulaValue', 'No formula')
            value = cell.get('formattedValue', 'N/A')

            print(f'  Column: {col_letter}')
            print(f'  Row 2 Formula: {formula}')
            print(f'  Row 2 Value: {value}')
        else:
            print('  Total Allowance column not found')

    print()
