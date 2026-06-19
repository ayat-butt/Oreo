#!/usr/bin/env python3
"""
Extract tax calculation logic from March 2026 payroll sheet.
Parse the FBR tax slab methodology from yellow columns.
"""

import json
import re
from pathlib import Path

# Read March 2026 sheet
march_file = r"C:\Users\ayat\.claude\projects\c--Agent-Oreo\8f5ed236-2497-4c4f-8480-c3b75b05ecce\tool-results\mcp-claude_ai_Google_Drive-read_file_content-1777354101731.txt"
april_file = r"C:\Users\ayat\.claude\projects\c--Agent-Oreo\8f5ed236-2497-4c4f-8480-c3b75b05ecce\tool-results\mcp-claude_ai_Google_Drive-read_file_content-1777354260459.txt"

def parse_sheet_json(filepath):
    """Parse Google Sheet JSON content into structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)

    # Extract markdown table from fileContent
    markdown = content.get('fileContent', '')
    lines = markdown.split('\n')

    # Parse header
    if len(lines) > 0:
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]  # Remove outer empty cells

        # Parse data rows (skip separator row at index 1)
        data = []
        for line in lines[2:]:
            if line.strip() and '|' in line:
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row = dict(zip(headers, cells))
                    data.append(row)

        return headers, data

    return [], []

print("=" * 80)
print("MARCH 2026 PAYROLL - TAX CALCULATION ANALYSIS")
print("=" * 80)

march_headers, march_data = parse_sheet_json(march_file)

print(f"\nFound {len(march_data)} employees in March 2026")
print(f"\nHeaders found: {len(march_headers)}")

# Find tax-related columns
tax_cols = [h for h in march_headers if 'tax' in h.lower() or 'taxable' in h.lower() or 'annual' in h.lower() or 'fbr' in h.lower()]
print(f"\nTax-related columns identified:")
for col in tax_cols:
    print(f"  - {col}")

# Show sample employee tax calculation (March)
print("\n" + "=" * 80)
print("SAMPLE EMPLOYEE - TAX CALCULATION BREAKDOWN (MARCH 2026)")
print("=" * 80)

if march_data:
    sample = march_data[0]  # First employee
    print(f"\nEmployee: {sample.get('Employee Name')}")
    print(f"Employee ID: {sample.get('Employee ID')}")
    print(f"Gross Salary: {sample.get('Gross Salary')}")
    print(f"Basic Salary: {sample.get('Basic Salary')}")
    print(f"Medical Allowance: {sample.get('Medical Allowance')}")
    print(f"Other Allowance: {sample.get('Other Allowance')}")
    print(f"Commute Allowance: {sample.get('Commute Allowance')}")
    print(f"Unpaid Days: {sample.get('Unpaid Days')}")
    print(f"\n--- TAX CALCULATION ---")
    print(f"Total Allowance: {sample.get('Total Allowance')}")
    print(f"Taxable Salary (March): {sample.get('Taxable Salary')}")
    print(f"Income Tax (March): {sample.get('Income Tax')}")
    print(f"\n--- ANNUAL TAX (FBR) ---")
    print(f"YTD Taxable (Jul–Feb): {sample.get('YTD Taxable (Jul–Feb)')}")
    print(f"Mar 2026 Taxable: {sample.get('Mar 2026 Taxable')}")
    print(f"Annual Taxable (Projected): {sample.get('Annual Taxable (Projected)')}")
    print(f"Annual Tax Liability (FBR): {sample.get('Annual Tax Liability (FBR)')}")
    print(f"Tax Collected So Far (Jul–Feb): {sample.get('Tax Collected So Far (Jul–Feb)')}")

# Extract high earners to understand tax slab
print("\n" + "=" * 80)
print("TAX CALCULATION PATTERNS - High Earners")
print("=" * 80)

# Sort by annual taxable to see patterns
sorted_data = sorted([d for d in march_data if d.get('Annual Taxable (Projected)')],
                     key=lambda x: float(re.sub(r'[^0-9]', '', x.get('Annual Taxable (Projected)', '0')) or 0),
                     reverse=True)

print("\nTop 5 earners (by Annual Taxable):")
for i, emp in enumerate(sorted_data[:5], 1):
    name = emp.get('Employee Name')
    annual_tax = emp.get('Annual Taxable (Projected)')
    tax_liability = emp.get('Annual Tax Liability (FBR)')
    tax_collected = emp.get('Tax Collected So Far (Jul–Feb)')

    print(f"\n{i}. {name}")
    print(f"   Annual Taxable: {annual_tax}")
    print(f"   Annual Tax Liability: {tax_liability}")
    print(f"   Tax Collected (Jul-Feb): {tax_collected}")

print("\n" + "=" * 80)
print("APRIL 2026 PAYROLL - INITIAL DATA CHECK")
print("=" * 80)

april_headers, april_data = parse_sheet_json(april_file)

print(f"\nFound {len(april_data)} employees in April 2026")
print(f"Headers: {len(april_headers)}")

# Compare March and April
march_names = {d['Employee Name'] for d in march_data if d.get('Employee Name')}
april_names = {d['Employee Name'] for d in april_data if d.get('Employee Name')}

new_employees = april_names - march_names
departed_employees = march_names - april_names

print(f"\nEMPLOYEE CHANGES:")
print(f"  New employees in April: {len(new_employees)}")
if new_employees:
    for name in sorted(new_employees):
        print(f"    + {name}")

print(f"\n  Departed employees: {len(departed_employees)}")
if departed_employees:
    for name in sorted(departed_employees):
        print(f"    - {name}")

print(f"\n  Total employees (March): {len(march_names)}")
print(f"  Total employees (April): {len(april_names)}")
print(f"  Continuing: {len(march_names & april_names)}")
