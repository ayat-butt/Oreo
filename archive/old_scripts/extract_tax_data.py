#!/usr/bin/env python3
"""
Extract employee tax data from three Google Sheets for income tax verification.
- April 2026 Payroll Sheet
- March 2026 Payroll Sheet
- Tax Working Sheet by Finance
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials as UserCredentials
from google.cloud import gspread
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# SHEET CONFIGURATIONS
# ─────────────────────────────────────────────────────────────────

SHEETS = {
    'April 2026': {
        'id': '1Cw3gIDpaMmhoJmo9rqN_f3KRwmTm9zR8cynDXrBN7aA',
        'gid': '1424468564',
        'name_col': 'A',  # Employee Name
        'taxable_col': 'R',  # Taxable Salary
        'tax_col': 'S',  # Income Tax
    },
    'March 2026': {
        'id': '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk',
        'gid': '1424468564',
        'name_col': 'A',
        'taxable_col': 'R',
        'tax_col': 'S',
    },
    'Tax Working Sheet': {
        'id': '1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs',
        'gid': '1035373631',
        'note': 'Extract all tax-related information',
    }
}

# ─────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────────

def authenticate_sheets():
    """Authenticate with Google Sheets API."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None

    # Try token.json first
    if os.path.exists('token.json'):
        creds = UserCredentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('sheets', 'v4', credentials=creds)

# ─────────────────────────────────────────────────────────────────
# DATA EXTRACTION
# ─────────────────────────────────────────────────────────────────

def extract_payroll_sheet(service, sheet_id, sheet_name, gid, name_col, taxable_col, tax_col):
    """Extract employee tax data from payroll sheets."""
    try:
        # Get all data from the sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A:Z"
        ).execute()

        values = result.get('values', [])

        if not values:
            print(f"❌ No data found in {sheet_name}")
            return None

        # Find column indices (assuming headers in row 1)
        headers = values[0] if values else []

        # Build result table
        data = []
        for row in values[1:]:  # Skip header row
            if len(row) > 0 and row[0].strip():  # Only non-empty rows
                employee_name = row[0] if len(row) > 0 else ""

                # Map column letters to indices
                taxable_idx = ord(taxable_col.upper()) - ord('A')
                tax_idx = ord(tax_col.upper()) - ord('A')

                taxable = row[taxable_idx] if len(row) > taxable_idx else ""
                tax = row[tax_idx] if len(row) > tax_idx else ""

                if employee_name.strip():
                    data.append({
                        'Employee Name': employee_name.strip(),
                        'Taxable Salary': taxable.strip(),
                        'Income Tax': tax.strip(),
                    })

        return data

    except Exception as e:
        print(f"❌ Error extracting from {sheet_name}: {e}")
        return None

def extract_tax_working_sheet(service, sheet_id, gid):
    """Extract all data from tax working sheet."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'Tax Working Sheet'!A:H"
        ).execute()

        values = result.get('values', [])

        if not values:
            print("❌ No data found in Tax Working Sheet")
            return None

        return values

    except Exception as e:
        print(f"❌ Error extracting Tax Working Sheet: {e}")
        return None

# ─────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────

def main():
    print("🔐 Authenticating with Google Sheets API...")
    service = authenticate_sheets()
    print("✅ Authentication successful\n")

    results = {}

    # Extract April 2026 Payroll
    print("📊 Extracting April 2026 Payroll Sheet...")
    april_data = extract_payroll_sheet(
        service,
        SHEETS['April 2026']['id'],
        'April 2026',
        SHEETS['April 2026']['gid'],
        SHEETS['April 2026']['name_col'],
        SHEETS['April 2026']['taxable_col'],
        SHEETS['April 2026']['tax_col'],
    )
    if april_data:
        results['April 2026'] = april_data
        print(f"✅ Extracted {len(april_data)} employees from April 2026\n")

    # Extract March 2026 Payroll
    print("📊 Extracting March 2026 Payroll Sheet...")
    march_data = extract_payroll_sheet(
        service,
        SHEETS['March 2026']['id'],
        'March 2026',
        SHEETS['March 2026']['gid'],
        SHEETS['March 2026']['name_col'],
        SHEETS['March 2026']['taxable_col'],
        SHEETS['March 2026']['tax_col'],
    )
    if march_data:
        results['March 2026'] = march_data
        print(f"✅ Extracted {len(march_data)} employees from March 2026\n")

    # Extract Tax Working Sheet
    print("📊 Extracting Tax Working Sheet...")
    tax_working = extract_tax_working_sheet(
        service,
        SHEETS['Tax Working Sheet']['id'],
        SHEETS['Tax Working Sheet']['gid'],
    )
    if tax_working:
        results['Tax Working Sheet'] = tax_working
        print(f"✅ Extracted data from Tax Working Sheet\n")

    # Save to JSON
    output_file = f"tax_verification_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"💾 Results saved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)

    if 'April 2026' in results:
        print(f"\n📅 April 2026 Payroll ({len(results['April 2026'])} employees):")
        df_april = pd.DataFrame(results['April 2026'])
        print(df_april.to_string(index=False))

    if 'March 2026' in results:
        print(f"\n📅 March 2026 Payroll ({len(results['March 2026'])} employees):")
        df_march = pd.DataFrame(results['March 2026'])
        print(df_march.to_string(index=False))

    if 'Tax Working Sheet' in results:
        print(f"\n📋 Tax Working Sheet Preview (first 20 rows):")
        for idx, row in enumerate(results['Tax Working Sheet'][:20]):
            print(row)

if __name__ == '__main__':
    main()
