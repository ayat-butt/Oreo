#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculate Income Tax for all 185 employees using Pakistan tax slabs
Based on Taxable Salary (Column Q)
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

PAYROLL_SHEET_ID = '1ghXhoMikgp09sOr65nRX5N4OgVb2uKkpATmF9ab-tmA'

print('=' * 100)
print('CALCULATING INCOME TAX FOR ALL 185 EMPLOYEES')
print('Pakistan Tax Slabs (FY 2025-2026)')
print('=' * 100)
print()

# Pakistan income tax slabs (as per payroll memory)
# Below 600,000: 0% (BTL)
# 600,001 - 1,200,000: 1%
# 1,200,001 - 2,200,000: 11% (Fixed 6,000 + excess × 11%)
# 2,200,001 - 3,200,000: 23% (Fixed 116,000 + excess × 23%)
# 3,200,001 - 4,100,000: 30% (Fixed 346,000 + excess × 30%)
# 4,100,001+: 35% (Fixed 616,000 + excess × 35%)

def calculate_tax(taxable_salary):
    """Calculate income tax based on Pakistan slabs"""
    try:
        ts = float(str(taxable_salary).replace(',', '').strip() or 0)
    except:
        return 0

    if ts <= 600000:
        return 0
    elif ts <= 1200000:
        return (ts - 600000) * 0.01
    elif ts <= 2200000:
        return 6000 + (ts - 1200000) * 0.11
    elif ts <= 3200000:
        return 116000 + (ts - 2200000) * 0.23
    elif ts <= 4100000:
        return 346000 + (ts - 3200000) * 0.30
    else:
        return 616000 + (ts - 4100000) * 0.35

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

total_calculated = 0

for entity in entities:
    print(f'{entity}:')
    print('-' * 100)

    result = service.spreadsheets().values().get(
        spreadsheetId=PAYROLL_SHEET_ID,
        range=f'{entity}!A1:AA500'
    ).execute()

    values = result.get('values', [])
    if not values:
        continue

    headers = values[0]
    col_map = {h: i for i, h in enumerate(headers)}

    name_idx = col_map.get('Employee Name', 1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    if taxable_idx < 0 or income_tax_idx < 0:
        print(f'  ❌ Missing columns')
        continue

    # Build batch update
    batch_requests = []
    entity_count = 0
    sample_calcs = []

    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        taxable_sal = row[taxable_idx] if taxable_idx < len(row) else ''

        if taxable_sal:
            tax_amount = calculate_tax(taxable_sal)
            batch_requests.append({
                'range': f'{entity}!{chr(65 + income_tax_idx)}{row_idx}',
                'values': [[round(tax_amount, 2)]]
            })
            entity_count += 1

            # Collect samples
            if len(sample_calcs) < 3:
                clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
                sample_calcs.append((clean_name, taxable_sal, round(tax_amount, 2)))

    # Execute batch update
    if batch_requests:
        body = {'data': batch_requests, 'valueInputOption': 'RAW'}
        response = service.spreadsheets().values().batchUpdate(
            spreadsheetId=PAYROLL_SHEET_ID,
            body=body
        ).execute()

        updated = response.get('totalUpdatedCells', 0)
        print(f'  [OK] Calculated and applied: {entity_count} employees')
        print()
        print(f'  Sample calculations:')
        for name, taxable, tax in sample_calcs:
            print(f'    {name}: Taxable={taxable}, Tax={tax}')
        print()

        total_calculated += entity_count

print('=' * 100)
print(f'[SUCCESS] TOTAL INCOME TAX CALCULATED & APPLIED: {total_calculated}/185 employees')
print('=' * 100)
