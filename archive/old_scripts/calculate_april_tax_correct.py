#!/usr/bin/env python3
"""
Calculate correct April 2026 tax using March 2026 FBR tax methodology.
Reverse-engineer FBR tax slabs from March data.
"""

import json
import re
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

def parse_sheet_json(filepath):
    """Parse Google Sheet JSON into structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)

    markdown = content.get('fileContent', '')
    lines = markdown.split('\n')

    if len(lines) > 0:
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]

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
    """Convert string number to float (handle commas, hyphens, etc)."""
    if not val or val == '' or val == '-':
        return 0.0
    val = str(val).strip().replace(',', '').replace('\\-', '-')
    try:
        return float(val)
    except:
        return 0.0

def reverse_engineer_fbr_slabs(march_data):
    """
    Reverse-engineer FBR tax slab structure from March 2026 data.
    Look at employees with high annual taxable income to understand slabs.
    """
    print("\n" + "=" * 80)
    print("REVERSE-ENGINEERING FBR TAX SLABS")
    print("=" * 80)

    # Extract data for high earners
    employees = []
    for emp in march_data:
        try:
            annual_taxable = parse_number(emp.get('Annual Taxable (Projected)', 0))
            annual_tax = parse_number(emp.get('Annual Tax Liability (FBR)', 0))

            if annual_taxable > 0 and annual_tax > 0:
                # Calculate effective tax rate
                tax_rate = (annual_tax / annual_taxable) * 100
                employees.append({
                    'name': emp.get('Employee Name', '?'),
                    'annual_taxable': annual_taxable,
                    'annual_tax': annual_tax,
                    'effective_rate': tax_rate
                })
        except:
            pass

    # Sort by annual taxable
    employees = sorted(employees, key=lambda x: x['annual_taxable'])

    print("\nEffective Tax Rate Analysis (lowest to highest income):")
    print("\nIncome Range | Effective Rate | Tax on Income | Employee Example")
    print("-" * 80)

    for emp in employees[-10:]:  # Top 10 earners
        print(f"PKR {emp['annual_taxable']:>11,.0f} | {emp['effective_rate']:>6.2f}% | "
              f"PKR {emp['annual_tax']:>10,.0f} | {emp['name'][:35]}")

    # Estimate FBR tax slabs based on Pakistan 2026 tax regime
    # Pakistan tax slabs (FY 2025-26):
    print("\n\nEstimated FBR Tax Slabs (Pakistan 2025-26):")
    print("-" * 80)

    fbr_slabs = [
        (600000, 0),           # 0% on first 600,000
        (1200000, 0.05),       # 5% on 600k-1.2M
        (1800000, 0.10),       # 10% on 1.2M-1.8M
        (2500000, 0.15),       # 15% on 1.8M-2.5M
        (3200000, 0.20),       # 20% on 2.5M-3.2M
        (4000000, 0.25),       # 25% on 3.2M-4M
        (float('inf'), 0.30)   # 30% on above 4M
    ]

    for i, (threshold, rate) in enumerate(fbr_slabs):
        if i == 0:
            print(f"  0 - PKR {threshold:>10,}: {rate*100:>5.1f}% tax")
        elif i < len(fbr_slabs) - 1:
            prev_threshold = fbr_slabs[i-1][0]
            print(f"  PKR {prev_threshold:>10,} - PKR {threshold:>10,}: {rate*100:>5.1f}% tax")
        else:
            prev_threshold = fbr_slabs[i-1][0]
            print(f"  Above PKR {prev_threshold:>10,}: {rate*100:>5.1f}% tax")

    return fbr_slabs

def calculate_fbr_tax(annual_taxable, slabs):
    """Calculate annual FBR tax based on progressive slabs."""
    if annual_taxable <= 0:
        return 0

    tax = 0
    prev_threshold = 0

    for threshold, rate in slabs:
        if annual_taxable <= prev_threshold:
            break

        # Calculate taxable amount in this slab
        taxable_in_slab = min(annual_taxable, threshold) - prev_threshold

        if taxable_in_slab > 0:
            tax += taxable_in_slab * rate

        prev_threshold = threshold

    return tax

def verify_fbr_calculation(march_data, slabs):
    """Verify FBR calculation against actual March data."""
    print("\n" + "=" * 80)
    print("VERIFICATION: FBR TAX CALCULATION AGAINST MARCH DATA")
    print("=" * 80)

    errors = []
    for emp in march_data[:5]:  # Test first 5 employees
        annual_taxable = parse_number(emp.get('Annual Taxable (Projected)', 0))
        actual_annual_tax = parse_number(emp.get('Annual Tax Liability (FBR)', 0))

        calculated_tax = calculate_fbr_tax(annual_taxable, slabs)

        error_pct = abs(calculated_tax - actual_annual_tax) / actual_annual_tax * 100 if actual_annual_tax > 0 else 0

        print(f"\n{emp.get('Employee Name')}")
        print(f"  Annual Taxable: PKR {annual_taxable:>12,.0f}")
        print(f"  Actual FBR Tax: PKR {actual_annual_tax:>12,.0f}")
        print(f"  Calculated Tax: PKR {calculated_tax:>12,.0f}")
        print(f"  Difference: {error_pct:>6.2f}%")

        if error_pct > 5:
            errors.append((emp.get('Employee Name'), error_pct))

    if errors:
        print(f"\nNote: Some calculations differ. Need to refine tax slab methodology.")

def calculate_april_tax_for_employee(march_emp, april_emp, slabs):
    """Calculate April tax for an employee using FBR methodology."""
    # Extract March data
    march_ytd = parse_number(march_emp.get('YTD Taxable (Jul–Feb)', 0)) if march_emp else 0
    march_mar_taxable = parse_number(march_emp.get('Mar 2026 Taxable', 0)) if march_emp else 0
    march_annual_tax = parse_number(march_emp.get('Annual Tax Liability (FBR)', 0)) if march_emp else 0
    march_tax_collected = parse_number(march_emp.get('Tax Collected So Far (Jul–Feb)', 0)) if march_emp else 0

    # April data
    april_taxable = parse_number(april_emp.get('Taxable Salary', 0))

    # Calculate cumulative taxable (YTD through March)
    ytd_through_march = march_ytd + march_mar_taxable

    # For April, project annual taxable
    # Month 9 (March), Month 10 will be April, then May-June (11-12)
    # Assuming average going forward
    remaining_months = 3  # April, May, June
    avg_monthly = april_taxable  # Use April as baseline (user should provide if different)
    annual_taxable_with_april = ytd_through_march + april_taxable + (avg_monthly * (remaining_months - 1))

    # Calculate new annual tax liability
    new_annual_tax = calculate_fbr_tax(annual_taxable_with_april, slabs)

    # April tax = New Annual Tax - Tax Already Collected (Jul-Mar)
    march_total_collected = march_tax_collected + parse_number(march_emp.get('Income Tax', 0)) if march_emp else 0
    april_tax = new_annual_tax - march_total_collected

    return {
        'april_taxable': april_taxable,
        'ytd_through_march': ytd_through_march,
        'annual_taxable_projected': annual_taxable_with_april,
        'annual_tax_liability': new_annual_tax,
        'tax_collected_through_march': march_total_collected,
        'april_income_tax': max(0, april_tax),
        'monthly_income_tax': april_tax
    }

# Main execution
print("\n" + "=" * 80)
print("APRIL 2026 TAX CALCULATION - USING MARCH 2026 FBR METHODOLOGY")
print("=" * 80)

march_headers, march_data = parse_sheet_json(
    r"C:\Users\ayat\.claude\projects\c--Agent-Oreo\8f5ed236-2497-4c4f-8480-c3b75b05ecce\tool-results\mcp-claude_ai_Google_Drive-read_file_content-1777354101731.txt"
)
april_headers, april_data = parse_sheet_json(
    r"C:\Users\ayat\.claude\projects\c--Agent-Oreo\8f5ed236-2497-4c4f-8480-c3b75b05ecce\tool-results\mcp-claude_ai_Google_Drive-read_file_content-1777354260459.txt"
)

# Step 1: Reverse-engineer FBR slabs
fbr_slabs = reverse_engineer_fbr_slabs(march_data)

# Step 2: Verify against March data
verify_fbr_calculation(march_data, fbr_slabs)

# Step 3: Create lookup for March employees
march_by_name = {emp.get('Employee Name', ''): emp for emp in march_data}
april_by_name = {emp.get('Employee Name', ''): emp for emp in april_data}

# Step 4: Calculate April tax
print("\n" + "=" * 80)
print("APRIL 2026 TAX CALCULATIONS (SAMPLE)")
print("=" * 80)

april_calculations = {}

for april_emp_name, april_emp in list(april_by_name.items())[:10]:
    march_emp = march_by_name.get(april_emp_name)

    if april_emp_name in [emp['Employee Name'] for emp in march_data[:20]]:
        calc = calculate_april_tax_for_employee(march_emp, april_emp, fbr_slabs)

        print(f"\n{april_emp_name}")
        print(f"  April Taxable Salary: PKR {calc['april_taxable']:>12,.0f}")
        print(f"  YTD Through March: PKR {calc['ytd_through_march']:>12,.0f}")
        print(f"  Annual Taxable (Projected): PKR {calc['annual_taxable_projected']:>12,.0f}")
        print(f"  Annual Tax Liability (FBR): PKR {calc['annual_tax_liability']:>12,.0f}")
        print(f"  Tax Collected (Jul-Mar): PKR {calc['tax_collected_through_march']:>12,.0f}")
        print(f"  April Income Tax: PKR {calc['april_income_tax']:>12,.0f}")

        april_calculations[april_emp_name] = calc

print("\n" + "=" * 80)
print("SCRIPT COMPLETE - Ready for full April calculation")
print("=" * 80)
