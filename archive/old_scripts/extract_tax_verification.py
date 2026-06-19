#!/usr/bin/env python
"""
Extract employee tax data from Google Sheets for income tax verification.
Uses the existing HR Assistant authentication setup.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add hr_assistant to path
sys.path.insert(0, str(Path(__file__).parent))

from hr_assistant.config import get_google_services

def extract_payroll_data(sheets_service, sheet_id, sheet_name):
    """Extract employee tax data from payroll sheet."""
    try:
        # Use different range format - try to get without sheet name quotes
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="A:S"
        ).execute()

        values = result.get('values', [])
        if not values:
            return None

        employees = []
        # Skip header row (row 1)
        for row_idx, row in enumerate(values[1:], start=2):
            if len(row) > 0 and row[0].strip():
                try:
                    # Column A (0) = Employee Name
                    # Column R (17) = Taxable Salary
                    # Column S (18) = Income Tax
                    name = row[0].strip() if len(row) > 0 else ""
                    taxable = row[17].strip() if len(row) > 17 else "—"
                    income_tax = row[18].strip() if len(row) > 18 else "—"

                    if name and name != 'Total' and not name.startswith('='):
                        employees.append({
                            'Employee Name': name,
                            'Taxable Salary': taxable,
                            'Income Tax': income_tax,
                        })
                except (IndexError, AttributeError):
                    pass

        return employees if employees else None

    except Exception as e:
        print(f"Error extracting from {sheet_name}: {e}")
        return None

def main():
    print("\n" + "="*80)
    print("GOOGLE SHEETS TAX VERIFICATION DATA EXTRACTION")
    print("="*80 + "\n")

    # Get authenticated services
    print("Authenticating with Google Sheets API...")
    try:
        services = get_google_services()
        sheets = services['sheets']
        print("[OK] Authentication successful\n")
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        sys.exit(1)

    # Sheet configurations
    sheets_to_extract = {
        'April 2026': '1Cw3gIDpaMmhoJmo9rqN_f3KRwmTm9zR8cynDXrBN7aA',
        'March 2026': '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk',
    }

    all_data = {}

    # Extract from each sheet
    for sheet_name, sheet_id in sheets_to_extract.items():
        print(f"Extracting {sheet_name} Payroll...")
        data = extract_payroll_data(sheets, sheet_id, sheet_name)

        if data:
            all_data[sheet_name] = data
            print(f"  [OK] Extracted {len(data)} employees\n")
        else:
            print(f"  [NO DATA] No data found\n")

    # Try to extract Tax Working Sheet
    print("Extracting Tax Working Sheet...")
    try:
        result = sheets.spreadsheets().values().get(
            spreadsheetId='1nw09utC0x3WFsTEM2Qj548y289FUoccPTW3jft3LeFs',
            range="A:H"
        ).execute()

        tax_values = result.get('values', [])
        if tax_values:
            all_data['Tax Working Sheet'] = tax_values
            print(f"  [OK] Extracted tax working sheet ({len(tax_values)} rows)\n")
        else:
            print(f"  [NO DATA] No data found\n")
    except Exception as e:
        print(f"  [ERROR] Error: {e}\n")

    # Save results
    if all_data:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'tax_verification_data_{timestamp}.json'

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Data saved to: {output_file}\n")

        # Print formatted tables
        print("="*80)
        print("APRIL 2026 PAYROLL - TAX VERIFICATION DATA")
        print("="*80 + "\n")

        if 'April 2026' in all_data:
            april_data = all_data['April 2026']
            print(f"{'Employee Name':<35} {'Taxable Salary':<20} {'Income Tax':<20}")
            print("-"*80)

            total_taxable = 0
            total_tax = 0

            for emp in april_data:
                name = emp['Employee Name']
                taxable = emp['Taxable Salary']
                tax = emp['Income Tax']

                print(f"{name:<35} {taxable:<20} {tax:<20}")

                # Try to sum numeric values
                try:
                    if taxable != '—':
                        total_taxable += float(taxable.replace(',', ''))
                except (ValueError, AttributeError):
                    pass

                try:
                    if tax != '—':
                        total_tax += float(tax.replace(',', ''))
                except (ValueError, AttributeError):
                    pass

            print("-"*80)
            print(f"{'TOTAL':<35} {total_taxable:>19,.0f} {total_tax:>19,.0f}\n")

        # March data
        print("\n" + "="*80)
        print("MARCH 2026 PAYROLL - TAX VERIFICATION DATA")
        print("="*80 + "\n")

        if 'March 2026' in all_data:
            march_data = all_data['March 2026']
            print(f"{'Employee Name':<35} {'Taxable Salary':<20} {'Income Tax':<20}")
            print("-"*80)

            total_taxable = 0
            total_tax = 0

            for emp in march_data:
                name = emp['Employee Name']
                taxable = emp['Taxable Salary']
                tax = emp['Income Tax']

                print(f"{name:<35} {taxable:<20} {tax:<20}")

                # Try to sum numeric values
                try:
                    if taxable != '—':
                        total_taxable += float(taxable.replace(',', ''))
                except (ValueError, AttributeError):
                    pass

                try:
                    if tax != '—':
                        total_tax += float(tax.replace(',', ''))
                except (ValueError, AttributeError):
                    pass

            print("-"*80)
            print(f"{'TOTAL':<35} {total_taxable:>19,.0f} {total_tax:>19,.0f}\n")

        # Tax Working Sheet preview
        if 'Tax Working Sheet' in all_data:
            print("\n" + "="*80)
            print("TAX WORKING SHEET - PREVIEW (First 10 rows)")
            print("="*80 + "\n")

            tax_sheet = all_data['Tax Working Sheet']
            for idx, row in enumerate(tax_sheet[:10]):
                print(f"Row {idx}: {row}")

    else:
        print("[ERROR] No data extracted from any sheet")
        sys.exit(1)

if __name__ == '__main__':
    main()
