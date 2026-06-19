#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract and refine employee tax data from March 2026 Tax Working Sheet.
Creates a clean CSV with all required columns for April 2026 tax deduction calculations.

Formula: April 2026 Tax = (New Annual Tax Liability - Tax Collected Jul-Mar) / 3
"""

import os
import csv
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Authenticate
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('sheets', 'v4', credentials=creds)

# Tax Working Sheet ID
TAX_SHEET_ID = '1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs'

print("[*] Fetching Tax Calculation data...")

# Get metadata to find correct sheet name
metadata = service.spreadsheets().get(spreadsheetId=TAX_SHEET_ID).execute()
sheets = metadata.get('sheets', [])

# Use Tax Calculation sheet
sheet_title = None
for sheet in sheets:
    if 'Tax Calculation' in sheet['properties']['title']:
        sheet_title = sheet['properties']['title']
        break

if not sheet_title:
    if len(sheets) > 1:
        sheet_title = sheets[1]['properties']['title']

print(f"[OK] Using sheet: {sheet_title}\n")

# Get all data
result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range=f"{sheet_title}!A1:Z200"
).execute()

values = result.get('values', [])

if not values:
    print("[ERROR] No data found")
    exit(1)

print(f"[OK] Retrieved {len(values)} rows\n")

# Parse headers
headers = values[0] if values else []
print("Column Headers:")
for idx, h in enumerate(headers):
    col_letter = chr(65 + idx)
    print(f"  [{idx}] {col_letter}: {h}")

print("\n" + "=" * 150)
print("Data Extraction")
print("=" * 150)

# Build CSV with extracted data
output_file = 'march_2026_tax_detailed.csv'

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Column mapping from Tax Calculation sheet:
    # B(1) = Employee Name
    # C(2) = Entity
    # D(3) = Yearly (Annual Taxable Projected)
    # L(11) = Total tax liability (Annual Tax Liability FBR)
    # M(12) = Tax Already Deducted (Jul-Feb cumulative tax)
    # O(14) = Current Month Tax (March calculated tax deduction)

    writer.writerow([
        'Employee Name',
        'Entity',
        'YTD Taxable (Jul-Feb) [Note: This is CUMULATIVE TAX, not taxable salary]',
        'Mar 2026 Tax Deduction [Current Month Calculation]',
        'Annual Taxable (Projected) [Full year estimate]',
        'Annual Tax Liability (FBR) [Total FBR tax for year]',
        'Tax Collected So Far (Jul-Feb) [Cumulative from 8 months]',
        'CALCULATION: April Tax = (Annual Tax - Tax Jul-Mar) / 3'
    ])

    # Skip header row, process employee rows
    employee_count = 0
    for row in values[1:]:
        if len(row) > 2 and row[1].strip() and row[2].strip() != 'Inactive':
            employee_count += 1

            name = row[1].strip() if len(row) > 1 else ''
            entity = row[2].strip() if len(row) > 2 else ''
            annual_taxable = row[3].strip() if len(row) > 3 else ''
            annual_tax = row[11].strip() if len(row) > 11 else ''
            tax_collected = row[12].strip() if len(row) > 12 else ''
            mar_tax = row[14].strip() if len(row) > 14 else ''

            if name:
                writer.writerow([
                    name,
                    entity,
                    tax_collected,
                    mar_tax,
                    annual_taxable,
                    annual_tax,
                    tax_collected,
                    'See formula in memory'
                ])

print(f"[OK] Extracted {employee_count} active employees")
print(f"[OK] Saved to: {output_file}\n")

# Print preview
print("=" * 150)
print("CSV Preview (first 15 rows):")
print("=" * 150)
with open(output_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for idx, line in enumerate(lines[:15]):
        print(line.rstrip())

print(f"\n[OK] Complete file has {len(lines)-1} data rows")
