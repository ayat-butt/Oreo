#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze March 2026 payroll tax calculation methodology
Study: YTD Taxable, Mar Taxable, Annual Taxable, Annual Tax Liability, Tax Collected So Far
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

print('=' * 160)
print('ANALYZING MARCH 2026 PAYROLL - TAX CALCULATION METHODOLOGY')
print('=' * 160)
print()

entities = ['NIETE_Islamabad', 'OPL', 'OWT', 'NIETE_Balochistan', 'Taleemabad_Inc_']

all_tax_data = []

for entity in entities:
    print(f'{entity}:')
    print()

    # Get all data up to column AI (which should have all tax columns)
    result = service.spreadsheets().values().get(
        spreadsheetId=MARCH_SHEET_ID,
        range=f'{entity}!A1:AI500'
    ).execute()

    values = result.get('values', [])
    if not values:
        print('  No data found\n')
        continue

    headers = values[0]
    col_map = {h.strip(): i for i, h in enumerate(headers)}

    # Print all headers to understand structure
    print('Available columns:')
    for idx, h in enumerate(headers):
        col_letter = chr(65 + idx) if idx < 26 else chr(64 + idx // 26) + chr(65 + idx % 26)
        print(f'  {col_letter}: {h}')
    print()

    # Get the column indices
    name_idx = col_map.get('Employee Name', 1)
    gross_idx = col_map.get('Gross Salary', -1)
    taxable_idx = col_map.get('Taxable Salary', -1)
    ytd_taxable_idx = col_map.get('YTD Taxable (Jul–Feb)', -1)
    mar_taxable_idx = col_map.get('Mar 2026 Taxable', -1)
    annual_taxable_idx = col_map.get('Annual Taxable (Projected)', -1)
    annual_tax_idx = col_map.get('Annual Tax Liability (FBR)', -1)
    tax_collected_idx = col_map.get('Tax Collected So Far (Jul–Feb)', -1)
    income_tax_idx = col_map.get('Income Tax', -1)

    # Show first 5 employees with all tax details
    sample_count = 0
    for row_idx, row in enumerate(values[1:], 2):
        emp_name = row[name_idx] if name_idx < len(row) else ''
        if not emp_name:
            continue

        gross = row[gross_idx] if gross_idx >= 0 and gross_idx < len(row) else ''
        taxable = row[taxable_idx] if taxable_idx >= 0 and taxable_idx < len(row) else ''
        ytd_taxable = row[ytd_taxable_idx] if ytd_taxable_idx >= 0 and ytd_taxable_idx < len(row) else ''
        mar_taxable = row[mar_taxable_idx] if mar_taxable_idx >= 0 and mar_taxable_idx < len(row) else ''
        annual_taxable = row[annual_taxable_idx] if annual_taxable_idx >= 0 and annual_taxable_idx < len(row) else ''
        annual_tax = row[annual_tax_idx] if annual_tax_idx >= 0 and annual_tax_idx < len(row) else ''
        tax_collected = row[tax_collected_idx] if tax_collected_idx >= 0 and tax_collected_idx < len(row) else ''
        income_tax = row[income_tax_idx] if income_tax_idx >= 0 and income_tax_idx < len(row) else ''

        if sample_count < 5:
            clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
            print(f'{sample_count + 1}. {clean_name}')
            print(f'   Gross Salary: {gross}')
            print(f'   Taxable Salary (Mar): {taxable}')
            print(f'   YTD Taxable (Jul-Feb): {ytd_taxable}')
            print(f'   Mar 2026 Taxable: {mar_taxable}')
            print(f'   Annual Taxable (Projected): {annual_taxable}')
            print(f'   Annual Tax Liability (FBR): {annual_tax}')
            print(f'   Tax Collected So Far (Jul-Feb): {tax_collected}')
            print(f'   March Income Tax: {income_tax}')
            print()

            # Try to reverse-engineer the calculation
            try:
                ytd_val = float(str(ytd_taxable).replace(',', '').strip()) if ytd_taxable else 0
                mar_val = float(str(mar_taxable).replace(',', '').strip()) if mar_taxable else 0
                annual_val = float(str(annual_taxable).replace(',', '').strip()) if annual_taxable else 0
                annual_tax_val = float(str(annual_tax).replace(',', '').strip()) if annual_tax else 0
                tax_coll_val = float(str(tax_collected).replace(',', '').strip()) if tax_collected else 0
                income_tax_val = float(str(income_tax).replace(',', '').strip()) if income_tax else 0

                # Check relationships
                if ytd_val > 0 and mar_val > 0 and annual_val > 0:
                    print(f'   ANALYSIS:')
                    print(f'     YTD + Mar = {ytd_val + mar_val:,.0f} (Annual projected: {annual_val:,.0f})')
                    print(f'     Annual Tax = {annual_tax_val:,.0f}')
                    print(f'     Tax collected so far = {tax_coll_val:,.0f}')
                    print(f'     Remaining tax = {annual_tax_val - tax_coll_val:,.0f}')
                    print(f'     March tax deducted = {income_tax_val:,.0f}')
                    print()

                all_tax_data.append({
                    'entity': entity,
                    'name': emp_name,
                    'gross': gross,
                    'ytd_taxable': ytd_val,
                    'mar_taxable': mar_val,
                    'annual_taxable': annual_val,
                    'annual_tax': annual_tax_val,
                    'tax_collected': tax_coll_val,
                    'march_income_tax': income_tax_val
                })

            except Exception as e:
                print(f'   Error parsing values: {e}')
                print()

            sample_count += 1

    print()

print()
print('=' * 160)
print('TAX CALCULATION LOGIC IDENTIFICATION')
print('=' * 160)
print()

if all_tax_data:
    print('Analyzing relationship between columns:')
    print()

    for data in all_tax_data[:3]:
        print(f'{data["name"]} ({data["entity"]}):')
        ytd = data['ytd_taxable']
        mar = data['mar_taxable']
        annual = data['annual_taxable']
        annual_tax = data['annual_tax']
        tax_coll = data['tax_collected']
        march_tax = data['march_income_tax']

        if annual > 0 and annual_tax > 0:
            tax_rate = (annual_tax / annual) * 100
            print(f'  Annual Tax Rate: {tax_rate:.2f}% of Annual Taxable')

        if annual_tax > 0 and tax_coll >= 0:
            remaining = annual_tax - tax_coll
            print(f'  Remaining Tax for Mar-Jun: {remaining:,.0f}')
            if remaining > 0:
                apr_tax = remaining / 4  # divided by 4 months
                print(f'  Estimated April tax (÷4): {apr_tax:,.0f}')

        print()
