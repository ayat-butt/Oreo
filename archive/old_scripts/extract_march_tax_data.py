#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract employee tax data from March 2026 Tax Working Sheet.
Required columns:
- Employee Name
- YTD Taxable (Jul-Feb)
- Mar 2026 Taxable
- Annual Taxable (Projected)
- Annual Tax Liability (FBR)
- Tax Collected So Far (Jul-Feb)
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

print("[*] Fetching Tax Working Sheet data...")

# First, get metadata to find correct sheet name
metadata = service.spreadsheets().get(spreadsheetId=TAX_SHEET_ID).execute()
sheets = metadata.get('sheets', [])
print(f"[INFO] Found {len(sheets)} sheet(s) in workbook:")
for sheet in sheets:
    print(f"  - {sheet['properties']['title']} (gid: {sheet['properties']['sheetId']})")

# Find the "Tax Calculation" sheet or use the second one
sheet_title = None
for sheet in sheets:
    if 'Tax Calculation' in sheet['properties']['title']:
        sheet_title = sheet['properties']['title']
        break

# If not found, use the second sheet
if not sheet_title:
    if len(sheets) > 1:
        sheet_title = sheets[1]['properties']['title']
    else:
        sheet_title = sheets[0]['properties']['title']

print(f"[*] Using sheet: {sheet_title}")

# Get all data - expand range to capture all columns
result = service.spreadsheets().values().get(
    spreadsheetId=TAX_SHEET_ID,
    range=f"{sheet_title}!A1:Z200"
).execute()

values = result.get('values', [])

if not values:
    print("[ERROR] No data found in Tax Working Sheet")
    exit(1)

print(f"[OK] Retrieved {len(values)} rows from Tax Working Sheet\n")

# Display structure
print("=" * 200)
print("Sheet Structure - First 5 rows:")
print("=" * 200)
for idx, row in enumerate(values[:5]):
    print(f"Row {idx}: {row}")

print(f"\n[INFO] Total rows: {len(values)}")
print(f"[INFO] Total columns: {len(values[0]) if values else 0}")

# Display all headers with column indices
if values and values[0]:
    print("\nColumn Headers:")
    headers = values[0]
    for col_idx, header in enumerate(headers):
        col_letter = chr(65 + col_idx)  # A=65
        print(f"  [{col_idx:2d}] {col_letter}: {header}")

# Build CSV with extracted data
output_file = 'march_2026_tax_working_data.csv'

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # Columns mapping from Tax Calculation sheet:
    # B = Employee Name
    # C = Entity
    # D = Yearly (Annual Taxable Projected)
    # L = Total tax liability (Annual Tax Liability FBR)
    # M = Tax Already Deducted (Jul-Feb, assuming this is YTD)
    # O = Current Month Tax (March 2026)
    writer.writerow(['Employee Name', 'Entity', 'YTD Taxable (Jul-Feb)', 'Mar 2026 Taxable',
                     'Annual Taxable (Projected)', 'Annual Tax Liability (FBR)',
                     'Tax Collected So Far (Jul-Feb)'])

    # Skip header row, process employee rows
    for row in values[1:]:
        if len(row) > 1 and row[1].strip():  # Check for employee name
            name = row[1].strip() if len(row) > 1 else ''
            entity = row[2].strip() if len(row) > 2 else ''
            annual_taxable = row[3].strip() if len(row) > 3 else ''  # Column D
            tax_collected = row[12].strip() if len(row) > 12 else ''  # Column M
            annual_tax = row[11].strip() if len(row) > 11 else ''  # Column L
            mar_taxable = row[14].strip() if len(row) > 14 else ''  # Column O

            if name and entity != 'Inactive':  # Skip inactive employees
                # YTD Taxable = Tax Already Deducted (which is cumulative)
                writer.writerow([name, entity, tax_collected, mar_taxable, annual_taxable, annual_tax, tax_collected])

print(f"\n[OK] Data extracted and saved to: {output_file}")

# Print preview
print("\n" + "=" * 120)
print("CSV Preview (first 10 data rows):")
print("=" * 120)
with open(output_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines[:11]:
        print(line.rstrip())
