#!/usr/bin/env python3
"""
Analyze special cases in March 2026 tax calculations.
Look at Comments column for clues about tax treatment.
"""

import json
import re
from decimal import Decimal

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

march_headers, march_data = parse_sheet_json(
    r"C:\Users\ayat\.claude\projects\c--Agent-Oreo\8f5ed236-2497-4c4f-8480-c3b75b05ecce\tool-results\mcp-claude_ai_Google_Drive-read_file_content-1777354101731.txt"
)

print("\n" + "=" * 100)
print("SPECIAL CASES IN MARCH 2026 - TAX TREATMENT ANALYSIS")
print("=" * 100)

# Analyze cases with comments
print("\nEMPLOYEES WITH SPECIAL NOTES IN COMMENTS:")
print("-" * 100)

special_employees = []
for emp in march_data:
    comment = emp.get('Comments', '').strip()
    if comment and comment != '':
        special_employees.append({
            'name': emp.get('Employee Name'),
            'comment': comment,
            'taxable': parse_number(emp.get('Taxable Salary', 0)),
            'income_tax': parse_number(emp.get('Income Tax', 0)),
            'ytd_taxable': parse_number(emp.get('YTD Taxable (Jul–Feb)', 0)),
            'mar_taxable': parse_number(emp.get('Mar 2026 Taxable', 0)),
            'annual_taxable': parse_number(emp.get('Annual Taxable (Projected)', 0)),
            'annual_tax': parse_number(emp.get('Annual Tax Liability (FBR)', 0)),
            'tax_collected': parse_number(emp.get('Tax Collected So Far (Jul–Feb)', 0))
        })

print(f"\nFound {len(special_employees)} employees with special comments\n")

for emp in special_employees[:15]:  # Show first 15
    print(f"\n{emp['name']}")
    print(f"  Comment: {emp['comment']}")
    print(f"  Mar Taxable: PKR {emp['mar_taxable']:>10,.0f} | Mar Tax: PKR {emp['income_tax']:>10,.0f}")
    print(f"  Annual Taxable: PKR {emp['annual_taxable']:>10,.0f} | Annual Tax: PKR {emp['annual_tax']:>10,.0f}")

# Analyze zero-tax employees
print("\n\n" + "=" * 100)
print("ZERO-TAX EMPLOYEES (Understanding Tax Exemption Criteria)")
print("=" * 100)

zero_tax_emps = []
for emp in march_data:
    annual_tax = parse_number(emp.get('Annual Tax Liability (FBR)', 0))
    annual_taxable = parse_number(emp.get('Annual Taxable (Projected)', 0))

    if annual_tax == 0 and annual_taxable > 0:
        zero_tax_emps.append({
            'name': emp.get('Employee Name'),
            'annual_taxable': annual_taxable,
            'joining_date': emp.get('Joining Date', ''),
            'comment': emp.get('Comments', '')
        })

print(f"\nFound {len(zero_tax_emps)} employees with 0 annual tax but positive taxable income\n")

# Group by income range
income_ranges = {
    'below_600k': [e for e in zero_tax_emps if e['annual_taxable'] < 600000],
    '600k_800k': [e for e in zero_tax_emps if 600000 <= e['annual_taxable'] < 800000],
    '800k_1m': [e for e in zero_tax_emps if 800000 <= e['annual_taxable'] < 1000000],
    'above_1m': [e for e in zero_tax_emps if e['annual_taxable'] >= 1000000]
}

for range_name, emps in income_ranges.items():
    if emps:
        print(f"\n{range_name.upper()}: {len(emps)} employees")
        for e in emps[:3]:
            print(f"  - {e['name']}: PKR {e['annual_taxable']:>10,.0f}")

# Analyze probation status
print("\n\n" + "=" * 100)
print("NEW/PROBATION EMPLOYEES (Joining late in FY)")
print("=" * 100)

import datetime

# Joining dates in current FY (after July 2025)
probation_emps = []
for emp in march_data:
    joining_str = emp.get('Joining Date', '')
    if joining_str and '2025' in joining_str:
        try:
            # Extract just the month-year
            if '12-01' in joining_str or '2025-12' in joining_str:  # Dec 2025 or later
                annual_taxable = parse_number(emp.get('Annual Taxable (Projected)', 0))
                annual_tax = parse_number(emp.get('Annual Tax Liability (FBR)', 0))
                ytd = parse_number(emp.get('YTD Taxable (Jul–Feb)', 0))

                probation_emps.append({
                    'name': emp.get('Employee Name'),
                    'joining': joining_str[:50],
                    'ytd': ytd,
                    'annual_taxable': annual_taxable,
                    'annual_tax': annual_tax,
                    'months_in_fy': 4 if '2025-12' in joining_str else 3
                })
        except:
            pass

if probation_emps:
    print(f"\nFound {len(probation_emps)} recent joiners")
    for e in probation_emps[:5]:
        print(f"  {e['name']} (Joined {e['joining']})")
        print(f"    Months in FY: {e['months_in_fy']} | Annual Taxable: PKR {e['annual_taxable']:>10,.0f} | Tax: PKR {e['annual_tax']:>10,.0f}")

# Advance/Salary taken analysis
print("\n\n" + "=" * 100)
print("ADVANCE SALARY / SPECIAL DEDUCTIONS")
print("=" * 100)

advance_emps = [e for e in march_data if 'advance' in e.get('Comments', '').lower()]

if advance_emps:
    print(f"\nFound {len(advance_emps)} employees with advance salary taken\n")
    for e in advance_emps[:5]:
        advance = parse_number(e.get('Advance', 0))
        net_salary = parse_number(e.get('Net Salary March', 0))
        total_deductions = parse_number(e.get('Total Deductions', 0))
        print(f"{e.get('Employee Name')}")
        print(f"  Advance: PKR {advance:>10,.0f}")
        print(f"  Total Deductions: PKR {total_deductions:>10,.0f}")
        print(f"  Net Salary: PKR {net_salary:>10,.0f}")

# Check if certain allowances might affect taxability
print("\n\n" + "=" * 100)
print("TAX IMPACT ANALYSIS - Allowances vs Tax")
print("=" * 100)

print("\nSample employees showing relationship between Taxable Salary and Tax:\n")

sample_emps = [e for e in march_data if parse_number(e.get('Annual Tax Liability (FBR)', 0)) > 100000]
sample_emps = sorted(sample_emps,
                    key=lambda x: parse_number(x.get('Annual Taxable (Projected)', 0)),
                    reverse=True)[:3]

for emp in sample_emps:
    mar_taxable = parse_number(emp.get('Mar 2026 Taxable', 0))
    mar_tax = parse_number(emp.get('Income Tax', 0))
    annual_tax = parse_number(emp.get('Annual Tax Liability (FBR)', 0))

    # Calculate effective monthly tax rate
    if mar_taxable > 0:
        mar_effective_rate = (mar_tax / mar_taxable) * 100
    else:
        mar_effective_rate = 0

    # Expected vs actual
    print(f"\n{emp.get('Employee Name')}")
    print(f"  March Taxable: PKR {mar_taxable:>10,.0f} | March Tax: PKR {mar_tax:>10,.0f} | Rate: {mar_effective_rate:>5.2f}%")
    print(f"  Annual Tax Liability: PKR {annual_tax:>10,.0f}")
    print(f"  Months working (projected): 12")
    print(f"  Expected annual tax (Mar tax × 12): PKR {(mar_tax * 12):>10,.0f}")
    print(f"  Difference: PKR {(annual_tax - mar_tax * 12):>10,.0f}")

print("\n\n" + "=" * 100)
print("KEY FINDINGS FOR APRIL CALCULATION")
print("=" * 100)

print("""
Based on March 2026 analysis:

1. TAX EXEMPTION THRESHOLD: Appears to be PKR 600,000 annual taxable
   - Employees below this have 0 tax even if income shows taxable amount

2. SPECIAL CASES:
   - Salary taken as advance: Tax calculated differently
   - New joiners (Dec 2025+): Prorated based on months worked
   - Commute allowance differences: Noted but tax calculated on full taxable

3. MONTHLY TAX CALCULATION:
   - Monthly tax is NOT simply annual tax / 12
   - Monthly tax = (Annual Tax Liability - Tax Collected YTD) / Remaining Months
   - OR Monthly tax derived from FBR slab calculation on YTD + current month

4. FOR APRIL 2026 CALCULATION:
   - New joiners from April: Calculate YTD = Taxable so far (single month)
   - Existing employees: Update YTD = Previous YTD + April taxable
   - Recalculate annual tax on cumulative through April + (May+June projections)
   - Monthly tax = New annual - Tax collected through March
""")
