#!/usr/bin/env python3
"""
CORRECT April 2026 Tax Calculation using March 2026 FBR methodology.
Key formula: April Tax = (Annual Tax based on 12-month projection) - (Tax Collected Jul-Mar)
"""

import json
import re
import csv
from pathlib import Path

def parse_sheet_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    markdown = content.get('fileContent', '')
    lines = markdown.split('\n')
    if len(lines) > 0:
        headers = [h.strip() for h in lines[0].split('|')[1:-1]]
        data = []
        for line in lines[2:]:
            if line.strip() and '|' in line:
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row = dict(zip(headers, cells))
                    data.append(row)
        return headers, data
    return [], []

def parse_number(val):
    if not val or val == '' or val == '-':
        return 0.0
    val = str(val).strip().replace(',', '').replace('\\-', '-')
    try:
        return float(val)
    except:
        return 0.0

def calculate_fbr_tax_correct(annual_taxable):
    """
    Calculate FBR tax using Pakistan 2025-26 slabs with 600k exemption.
    Based on observed March 2026 patterns.
    """
    # PKR 600,000 exemption threshold
    if annual_taxable <= 600000:
        return 0

    # FBR Progressive Tax Slabs (for amount above 600k)
    # 0 - 600k: 0% (exempted)
    # 600k - 1.2M: 5% (on amount above 600k)
    # 1.2M - 1.8M: 10%
    # 1.8M - 2.5M: 15%
    # 2.5M - 3.2M: 20%
    # 3.2M - 4M: 25%
    # Above 4M: 30%

    tax = 0

    # First 600k: 0%
    if annual_taxable > 600000:
        slab1 = min(annual_taxable - 600000, 600000)  # 600k-1.2M
        tax += slab1 * 0.05

    if annual_taxable > 1200000:
        slab2 = min(annual_taxable - 1200000, 600000)  # 1.2M-1.8M
        tax += slab2 * 0.10

    if annual_taxable > 1800000:
        slab3 = min(annual_taxable - 1800000, 700000)  # 1.8M-2.5M
        tax += slab3 * 0.15

    if annual_taxable > 2500000:
        slab4 = min(annual_taxable - 2500000, 700000)  # 2.5M-3.2M
        tax += slab4 * 0.20

    if annual_taxable > 3200000:
        slab5 = min(annual_taxable - 3200000, 800000)  # 3.2M-4M
        tax += slab5 * 0.25

    if annual_taxable > 4000000:
        slab6 = annual_taxable - 4000000  # Above 4M
        tax += slab6 * 0.30

    return tax

# Parse both sheets
print("\n" + "=" * 100)
print("APRIL 2026 PAYROLL - CORRECT TAX CALCULATION")
print("=" * 100)

march_headers, march_data = parse_sheet_json(
    r"C:\Users\ayat\.claude\projects\c--Agent-Oreo\8f5ed236-2497-4c4f-8480-c3b75b05ecce\tool-results\mcp-claude_ai_Google_Drive-read_file_content-1777354101731.txt"
)
april_headers, april_data = parse_sheet_json(
    r"C:\Users\ayat\.claude\projects\c--Agent-Oreo\8f5ed236-2497-4c4f-8480-c3b75b05ecce\tool-results\mcp-claude_ai_Google_Drive-read_file_content-1777354260459.txt"
)

# Create lookups
march_by_name = {emp.get('Employee Name', ''): emp for emp in march_data}
april_by_name = {emp.get('Employee Name', ''): emp for emp in april_data}

# Verify FBR calculation against March data
print("\nVERIFYING FBR TAX CALCULATION AGAINST MARCH DATA:")
print("-" * 100)

test_count = 0
matched_count = 0

for emp_name, march_emp in list(march_by_name.items())[:20]:
    annual_taxable = parse_number(march_emp.get('Annual Taxable (Projected)', 0))
    actual_annual_tax = parse_number(march_emp.get('Annual Tax Liability (FBR)', 0))

    if annual_taxable > 0:
        calculated_tax = calculate_fbr_tax_correct(annual_taxable)
        error_pct = abs(calculated_tax - actual_annual_tax) / actual_annual_tax * 100 if actual_annual_tax > 0 else 0

        test_count += 1
        if error_pct < 5:
            matched_count += 1

if test_count > 0:
    print(f"Match rate: {matched_count}/{test_count} ({100*matched_count/test_count:.1f}%)")

# Calculate April taxes
print("\n\n" + "=" * 100)
print("APRIL 2026 TAX CALCULATIONS - ALL EMPLOYEES")
print("=" * 100)

april_results = []

for april_emp_name, april_emp in april_by_name.items():
    march_emp = march_by_name.get(april_emp_name)

    april_taxable = parse_number(april_emp.get('Taxable Salary', 0))

    if march_emp:
        # Existing employee
        march_ytd = parse_number(march_emp.get('YTD Taxable (Jul–Feb)', 0))
        march_mar_taxable = parse_number(march_emp.get('Mar 2026 Taxable', 0))
        march_tax_collected = parse_number(march_emp.get('Tax Collected So Far (Jul–Feb)', 0))
        march_income_tax = parse_number(march_emp.get('Income Tax', 0))

        # YTD through March
        ytd_through_march = march_ytd + march_mar_taxable

        # Project annual (April is month 10, May 11, June 12)
        # Assume April taxable = April amount, May-June = same as April
        annual_taxable_projected = ytd_through_march + april_taxable + (april_taxable * 2)

        # Calculate new annual tax
        annual_tax_new = calculate_fbr_tax_correct(annual_taxable_projected)

        # Total tax collected through March (includes July-Feb YTD + March)
        total_tax_collected_through_march = march_tax_collected + march_income_tax

        # April tax = New annual - Collected through March
        april_tax = annual_tax_new - total_tax_collected_through_march

        # Ensure non-negative
        april_tax = max(0, april_tax)

        employee_type = "Existing"

    else:
        # New employee in April (no March data)
        # For new joiners, YTD = April only (they just started)
        ytd_through_march = 0
        annual_taxable_projected = april_taxable * 9  # 9 remaining months (Apr-Dec)
        annual_tax_new = calculate_fbr_tax_correct(annual_taxable_projected)
        total_tax_collected_through_march = 0
        april_tax = max(0, annual_tax_new)

        employee_type = "New Joiner"

    april_results.append({
        'name': april_emp_name,
        'type': employee_type,
        'april_taxable': april_taxable,
        'ytd_through_march': ytd_through_march,
        'annual_taxable': annual_taxable_projected,
        'annual_tax': annual_tax_new,
        'tax_collected_through_march': total_tax_collected_through_march,
        'april_tax': april_tax
    })

# Sort by april tax (highest first)
april_results.sort(key=lambda x: x['april_tax'], reverse=True)

# Display results
print(f"\nCalculated tax for {len(april_results)} employees\n")
print(f"{'Employee Name':<40} | {'Type':<12} | {'Apr Taxable':<12} | {'Annual Tax':<12} | {'Apr Tax':<12}")
print("-" * 100)

for res in april_results:
    try:
        name = res['name'][:40] if res['name'] else "Unknown"
        print(f"{name:<40} | {res['type']:<12} | "
              f"PKR {res['april_taxable']:>10,.0f} | PKR {res['annual_tax']:>10,.0f} | "
              f"PKR {res['april_tax']:>10,.0f}")
    except:
        print(f"[Unicode error in name] | {res['type']:<12} | "
              f"PKR {res['april_taxable']:>10,.0f} | PKR {res['annual_tax']:>10,.0f} | "
              f"PKR {res['april_tax']:>10,.0f}")

# Summary statistics
print("\n\n" + "=" * 100)
print("SUMMARY STATISTICS")
print("=" * 100)

total_april_tax = sum(r['april_tax'] for r in april_results)
total_april_taxable = sum(r['april_taxable'] for r in april_results)

zero_tax_count = len([r for r in april_results if r['april_tax'] == 0])
positive_tax_count = len([r for r in april_results if r['april_tax'] > 0])

new_joiner_count = len([r for r in april_results if r['type'] == 'New Joiner'])
existing_count = len([r for r in april_results if r['type'] == 'Existing'])

print(f"\nTotal Employees: {len(april_results)}")
print(f"  - Existing: {existing_count}")
print(f"  - New Joiners: {new_joiner_count}")

print(f"\nTotal April Taxable Salary: PKR {total_april_taxable:>15,.0f}")
print(f"Total April Income Tax: PKR {total_april_tax:>15,.0f}")

if total_april_taxable > 0:
    avg_tax_rate = (total_april_tax / total_april_taxable) * 100
    print(f"Average Effective Tax Rate: {avg_tax_rate:>6.2f}%")

print(f"\nEmployees with 0 tax: {zero_tax_count}")
print(f"Employees with positive tax: {positive_tax_count}")

# Top 10 tax payers
print(f"\nTop 10 Tax Payers (April 2026):")
print("-" * 100)

for i, res in enumerate(april_results[:10], 1):
    print(f"{i:2d}. {res['name']:<38} | April Tax: PKR {res['april_tax']:>12,.0f}")

# Export to CSV for verification
output_file = r"C:\Agent Oreo\output\april_2026_tax_calculations.csv"
Path(r"C:\Agent Oreo\output").mkdir(parents=True, exist_ok=True)

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'Employee Name', 'Type', 'April Taxable', 'YTD Through March',
        'Annual Taxable Projected', 'Annual Tax Liability',
        'Tax Collected Through March', 'April Income Tax'
    ])
    writer.writeheader()

    for res in april_results:
        writer.writerow({
            'Employee Name': res['name'],
            'Type': res['type'],
            'April Taxable': f"{res['april_taxable']:.0f}",
            'YTD Through March': f"{res['ytd_through_march']:.0f}",
            'Annual Taxable Projected': f"{res['annual_taxable']:.0f}",
            'Annual Tax Liability': f"{res['annual_tax']:.0f}",
            'Tax Collected Through March': f"{res['tax_collected_through_march']:.0f}",
            'April Income Tax': f"{res['april_tax']:.0f}"
        })

print(f"\n\nResults exported to: {output_file}")

print("\n" + "=" * 100)
print("CALCULATION COMPLETE")
print("=" * 100)
