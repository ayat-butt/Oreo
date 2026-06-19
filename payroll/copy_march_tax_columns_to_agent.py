#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copy March tax calculation columns to Agent payroll sheet
Columns: YTD Taxable (Jul–Feb), Mar 2026 Taxable, Annual Taxable (Projected), Annual Tax Liability (FBR), Tax Collected So Far (Jul–Feb)
Then calculate April tax using: (Annual Tax Liability - Tax Collected So Far) ÷ 4
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

MARCH_SHEET_ID = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
AGENT_PAYROLL_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'
entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

print('=' * 120)
print('COPYING MARCH TAX CALCULATION COLUMNS TO AGENT PAYROLL')
print('=' * 120)
print()

print('Columns to copy:')
print('  - YTD Taxable (Jul–Feb)')
print('  - Mar 2026 Taxable')
print('  - Annual Taxable (Projected)')
print('  - Annual Tax Liability (FBR)')
print('  - Tax Collected So Far (Jul–Feb)')
print()
print('Then calculate April Tax using: (Annual Tax Liability - Tax Collected So Far) ÷ 4')
print()

total_processed = 0
total_april_tax_updated = 0

for entity in entities:
    print(f'{entity}:')

    # Load March data
    march_result = service.spreadsheets().values().get(
        spreadsheetId=MARCH_SHEET_ID,
        range=f'{entity}!A1:AI500'
    ).execute()

    march_values = march_result.get('values', [])
    if not march_values:
        print('  No March data found')
        continue

    march_headers = march_values[0]
    march_col_map = {h.strip(): i for i, h in enumerate(march_headers)}

    # Load Agent data
    agent_result = service.spreadsheets().values().get(
        spreadsheetId=AGENT_PAYROLL_ID,
        range=f'{entity}!A1:AI500'
    ).execute()

    agent_values = agent_result.get('values', [])
    if not agent_values:
        print('  No Agent data found')
        continue

    agent_headers = agent_values[0]
    agent_col_map = {h.strip(): i for i, h in enumerate(agent_headers)}

    # Get column indices from March
    march_name_idx = march_col_map.get('Employee Name', 1)
    march_ytd_idx = march_col_map.get('YTD Taxable (Jul–Feb)', -1)
    march_mar_taxable_idx = march_col_map.get('Mar 2026 Taxable', -1)
    march_annual_taxable_idx = march_col_map.get('Annual Taxable (Projected)', -1)
    march_annual_tax_idx = march_col_map.get('Annual Tax Liability (FBR)', -1)
    march_tax_collected_idx = march_col_map.get('Tax Collected So Far (Jul–Feb)', -1)

    # Get column indices from Agent
    agent_name_idx = agent_col_map.get('Employee Name', 1)
    agent_ytd_idx = agent_col_map.get('YTD Taxable (Jul–Feb)', -1)
    agent_mar_taxable_idx = agent_col_map.get('Mar 2026 Taxable', -1)
    agent_annual_taxable_idx = agent_col_map.get('Annual Taxable (Projected)', -1)
    agent_annual_tax_idx = agent_col_map.get('Annual Tax Liability (FBR)', -1)
    agent_tax_collected_idx = agent_col_map.get('Tax Collected So Far (Jul–Feb)', -1)
    agent_income_tax_idx = agent_col_map.get('Income Tax', -1)

    # Build mapping of employees from March
    march_data = {}
    for march_row in march_values[1:]:
        emp_name = march_row[march_name_idx] if march_name_idx < len(march_row) else ''
        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()
        march_data[emp_name_lower] = {
            'ytd': march_row[march_ytd_idx] if march_ytd_idx >= 0 and march_ytd_idx < len(march_row) else '',
            'mar_taxable': march_row[march_mar_taxable_idx] if march_mar_taxable_idx >= 0 and march_mar_taxable_idx < len(march_row) else '',
            'annual_taxable': march_row[march_annual_taxable_idx] if march_annual_taxable_idx >= 0 and march_annual_taxable_idx < len(march_row) else '',
            'annual_tax': march_row[march_annual_tax_idx] if march_annual_tax_idx >= 0 and march_annual_tax_idx < len(march_row) else '',
            'tax_collected': march_row[march_tax_collected_idx] if march_tax_collected_idx >= 0 and march_tax_collected_idx < len(march_row) else ''
        }

    # Build batch requests for Agent sheet
    batch_requests = []
    entity_count = 0

    for agent_row_idx, agent_row in enumerate(agent_values[1:], 2):
        emp_name = agent_row[agent_name_idx] if agent_name_idx < len(agent_row) else ''
        if not emp_name:
            continue

        emp_name_lower = emp_name.lower()

        # Find matching March data
        if emp_name_lower not in march_data:
            continue

        march_emp = march_data[emp_name_lower]

        # Add to batch requests - copy all 5 columns
        if agent_ytd_idx >= 0:
            col_letter = chr(65 + agent_ytd_idx) if agent_ytd_idx < 26 else chr(64 + agent_ytd_idx // 26) + chr(65 + agent_ytd_idx % 26)
            batch_requests.append({
                'range': f'{entity}!{col_letter}{agent_row_idx}',
                'values': [[march_emp['ytd']]]
            })

        if agent_mar_taxable_idx >= 0:
            col_letter = chr(65 + agent_mar_taxable_idx) if agent_mar_taxable_idx < 26 else chr(64 + agent_mar_taxable_idx // 26) + chr(65 + agent_mar_taxable_idx % 26)
            batch_requests.append({
                'range': f'{entity}!{col_letter}{agent_row_idx}',
                'values': [[march_emp['mar_taxable']]]
            })

        if agent_annual_taxable_idx >= 0:
            col_letter = chr(65 + agent_annual_taxable_idx) if agent_annual_taxable_idx < 26 else chr(64 + agent_annual_taxable_idx // 26) + chr(65 + agent_annual_taxable_idx % 26)
            batch_requests.append({
                'range': f'{entity}!{col_letter}{agent_row_idx}',
                'values': [[march_emp['annual_taxable']]]
            })

        if agent_annual_tax_idx >= 0:
            col_letter = chr(65 + agent_annual_tax_idx) if agent_annual_tax_idx < 26 else chr(64 + agent_annual_tax_idx // 26) + chr(65 + agent_annual_tax_idx % 26)
            batch_requests.append({
                'range': f'{entity}!{col_letter}{agent_row_idx}',
                'values': [[march_emp['annual_tax']]]
            })

        if agent_tax_collected_idx >= 0:
            col_letter = chr(65 + agent_tax_collected_idx) if agent_tax_collected_idx < 26 else chr(64 + agent_tax_collected_idx // 26) + chr(65 + agent_tax_collected_idx % 26)
            batch_requests.append({
                'range': f'{entity}!{col_letter}{agent_row_idx}',
                'values': [[march_emp['tax_collected']]]
            })

        # Calculate April tax = (Annual Tax - Tax Collected) ÷ 4
        if agent_income_tax_idx >= 0:
            try:
                annual_tax_num = float(str(march_emp['annual_tax']).replace(',', '').strip()) if march_emp['annual_tax'] else 0
                tax_collected_num = float(str(march_emp['tax_collected']).replace(',', '').strip()) if march_emp['tax_collected'] else 0
                april_tax = (annual_tax_num - tax_collected_num) / 4
            except:
                april_tax = 0

            col_letter = chr(65 + agent_income_tax_idx) if agent_income_tax_idx < 26 else chr(64 + agent_income_tax_idx // 26) + chr(65 + agent_income_tax_idx % 26)
            batch_requests.append({
                'range': f'{entity}!{col_letter}{agent_row_idx}',
                'values': [[april_tax]]
            })
            total_april_tax_updated += 1

        entity_count += 1

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=AGENT_PAYROLL_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  Processed {entity_count} employees')
        print(f'  Updated {updated} cells')
        total_processed += entity_count

print()
print('=' * 120)
print('SUMMARY')
print('=' * 120)
print()
print(f'Total employees processed: {total_processed}')
print(f'Total April tax calculations: {total_april_tax_updated}')
print()
print('[COMPLETE] March tax calculation columns copied to Agent payroll')
print('April income tax now calculated as: (Annual Tax Liability - Tax Collected So Far) ÷ 4')
print()
