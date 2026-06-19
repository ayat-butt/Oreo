#!/usr/bin/env python
"""
Extract employee tax data using direct HTTP requests to Google Sheets API.
"""

import json
import sys
import os

# Check if we have existing token
try:
    if os.path.exists('token.json'):
        with open('token.json', 'r') as f:
            token_data = json.load(f)
            access_token = token_data.get('access_token')
            if access_token:
                print(f"Using existing token")
    else:
        print("ERROR: token.json not found. Please run Google auth first.")
        sys.exit(1)
except Exception as e:
    print(f"Error reading token: {e}")
    sys.exit(1)

# Sheet configurations
sheets_config = {
    'April 2026': {
        'id': '1Cw3gIDpaMmhoJmo9rqN_f3KRwmTm9zR8cynDXrBN7aA',
        'range': "'April 2026'!A:S"
    },
    'March 2026': {
        'id': '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk',
        'range': "'March 2026'!A:S"
    },
}

import urllib.request
import urllib.error

def fetch_sheet_data(sheet_id, range_name, access_token):
    """Fetch data from Google Sheet using REST API."""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(range_name)}"
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data.get('values', [])
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error fetching sheet: {e}")
        return None

# Main execution
print("Extracting tax verification data from Google Sheets...\n")

results = {}

try:
    with open('token.json', 'r') as f:
        token_data = json.load(f)
        access_token = token_data.get('access_token')
except Exception as e:
    print(f"Error reading token: {e}")
    sys.exit(1)

import urllib.parse

# Extract April 2026
print("Fetching April 2026 Payroll Sheet...")
april_values = fetch_sheet_data(
    sheets_config['April 2026']['id'],
    sheets_config['April 2026']['range'],
    access_token
)

if april_values:
    april_data = []
    headers = april_values[0] if april_values else []

    for row in april_values[1:]:
        if len(row) > 0 and row[0].strip():
            try:
                # Column indices: A=0, R=17, S=18
                name = row[0] if len(row) > 0 else ""
                taxable = row[17] if len(row) > 17 else ""
                tax = row[18] if len(row) > 18 else ""

                if name.strip():
                    april_data.append({
                        'Employee Name': name.strip(),
                        'Taxable Salary': taxable.strip() if taxable else "—",
                        'Income Tax': tax.strip() if tax else "—"
                    })
            except IndexError:
                pass

    if april_data:
        results['April 2026'] = april_data
        print(f"✅ Extracted {len(april_data)} employees from April 2026")
else:
    print("❌ Failed to fetch April 2026 data")

print()

# Extract March 2026
print("Fetching March 2026 Payroll Sheet...")
march_values = fetch_sheet_data(
    sheets_config['March 2026']['id'],
    sheets_config['March 2026']['range'],
    access_token
)

if march_values:
    march_data = []
    headers = march_values[0] if march_values else []

    for row in march_values[1:]:
        if len(row) > 0 and row[0].strip():
            try:
                # Column indices: A=0, R=17, S=18
                name = row[0] if len(row) > 0 else ""
                taxable = row[17] if len(row) > 17 else ""
                tax = row[18] if len(row) > 18 else ""

                if name.strip():
                    march_data.append({
                        'Employee Name': name.strip(),
                        'Taxable Salary': taxable.strip() if taxable else "—",
                        'Income Tax': tax.strip() if tax else "—"
                    })
            except IndexError:
                pass

    if march_data:
        results['March 2026'] = march_data
        print(f"✅ Extracted {len(march_data)} employees from March 2026")
else:
    print("❌ Failed to fetch March 2026 data")

# Save results
if results:
    output_file = 'tax_verification_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Data saved to {output_file}")

    # Print summary tables
    print("\n" + "="*80)
    print("APRIL 2026 PAYROLL - TAX VERIFICATION DATA")
    print("="*80)
    if 'April 2026' in results:
        april_data = results['April 2026']
        print(f"\n{'Employee Name':<35} {'Taxable Salary':<20} {'Income Tax':<20}")
        print("-"*80)
        for emp in april_data:
            print(f"{emp['Employee Name']:<35} {emp['Taxable Salary']:<20} {emp['Income Tax']:<20}")
        print(f"\nTotal Employees: {len(april_data)}")

    print("\n" + "="*80)
    print("MARCH 2026 PAYROLL - TAX VERIFICATION DATA")
    print("="*80)
    if 'March 2026' in results:
        march_data = results['March 2026']
        print(f"\n{'Employee Name':<35} {'Taxable Salary':<20} {'Income Tax':<20}")
        print("-"*80)
        for emp in march_data:
            print(f"{emp['Employee Name']:<35} {emp['Taxable Salary']:<20} {emp['Income Tax']:<20}")
        print(f"\nTotal Employees: {len(march_data)}")
else:
    print("\n❌ No data extracted")
    sys.exit(1)
