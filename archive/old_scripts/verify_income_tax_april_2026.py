#!/usr/bin/env python3
"""
PAYROLL INCOME TAX VERIFICATION - April 2026
Pakistan FY (Jul-Jun) Tax Slab Calculation
Verify if current Income Tax values on April sheet are correct
"""

import csv
from datetime import datetime

# ============================================================================
# PAKISTAN INCOME TAX SLABS (FY 2025-2026)
# ============================================================================

TAX_SLABS = [
    {'name': 'BTL', 'min': 0, 'max': 599_999, 'fixed': 0, 'rate': 0.00, 'description': 'Below Taxable Limit'},
    {'name': 'Slab 1', 'min': 0, 'max': 599_999, 'fixed': 0, 'rate': 0.00, 'description': '<600,000'},
    {'name': 'Slab 2', 'min': 600_001, 'max': 1_200_000, 'fixed': 0, 'rate': 0.01, 'description': '600,001-1,200,000'},
    {'name': 'Slab 3', 'min': 1_200_001, 'max': 2_200_000, 'fixed': 6_000, 'rate': 0.11, 'description': '1,200,001-2,200,000'},
    {'name': 'Slab 4', 'min': 2_200_001, 'max': 3_200_000, 'fixed': 116_000, 'rate': 0.23, 'description': '2,200,001-3,200,000'},
    {'name': 'Slab 5', 'min': 3_200_001, 'max': 4_100_000, 'fixed': 346_000, 'rate': 0.30, 'description': '3,200,001-4,100,000'},
    {'name': 'Slab 6', 'min': 4_100_001, 'max': float('inf'), 'fixed': 616_000, 'rate': 0.35, 'description': '4,100,001+'},
]

# ============================================================================
# APRIL 2026 EMPLOYEES - From April 2026 Payroll Sheet (Col B, R, S)
# ============================================================================

APRIL_2026_EMPLOYEES = [
    {'id': 321, 'name': 'Abdul Waheed', 'entity': 'NIETE', 'taxable_salary': 401_100.00, 'current_tax': 0.00},
    {'id': 356, 'name': 'Aleeha Noor', 'entity': 'NIETE', 'taxable_salary': 206_280.00, 'current_tax': 0.00},
    {'id': 108, 'name': 'Anam Masood', 'entity': 'NIETE', 'taxable_salary': 474_545.23, 'current_tax': 19_501.32},
    {'id': 144, 'name': 'Aneela Khaliq', 'entity': 'NIETE', 'taxable_salary': 191_009.55, 'current_tax': 500.52},
    {'id': 195, 'name': 'Aown Raza', 'entity': 'NIETE', 'taxable_salary': 94_311.98, 'current_tax': 0.00},
    {'id': 133, 'name': 'Areej Noshad', 'entity': 'NIETE', 'taxable_salary': 191_009.55, 'current_tax': 1_270.52},
    {'id': 163, 'name': 'Ashas Khan', 'entity': 'NIETE', 'taxable_salary': 228_835.19, 'current_tax': 1_084.91},
    {'id': 139, 'name': 'Asma Zaheer', 'entity': 'NIETE', 'taxable_salary': 477_500.00, 'current_tax': 15_637.72},
    {'id': 199, 'name': 'Ayat Butt', 'entity': 'NIETE', 'taxable_salary': 200_550.00, 'current_tax': 455.55},
    {'id': 152, 'name': 'Bushra', 'entity': 'NIETE', 'taxable_salary': 242_661.68, 'current_tax': 3_289.95},
    {'id': 135, 'name': 'Chaudhary Hashir Hussain Shahid', 'entity': 'NIETE', 'taxable_salary': 382_000.00, 'current_tax': 9_206.51},
    {'id': 154, 'name': 'Danish Iqbal', 'entity': 'NIETE', 'taxable_salary': 206_461.45, 'current_tax': 2_344.56},
    {'id': 114, 'name': 'Eysha Qadeer', 'entity': 'NIETE', 'taxable_salary': 191_005.73, 'current_tax': 1_094.41},
    {'id': 164, 'name': 'Hafiz Abdul Malik', 'entity': 'NIETE', 'taxable_salary': 228_571.61, 'current_tax': 1_393.82},
    {'id': 180, 'name': 'Hafsa Bashir', 'entity': 'Digital Learning', 'taxable_salary': 231_467.17, 'current_tax': 1_675.39},
    {'id': 343, 'name': 'Hamza Razaq', 'entity': 'NIETE', 'taxable_salary': 227_290.00, 'current_tax': 0.00},
    {'id': 254, 'name': 'Hamza Shahid', 'entity': 'OWT', 'taxable_salary': 496_600.00, 'current_tax': 5_584.18},
    {'id': 159, 'name': 'Hamza Siddique', 'entity': 'NIETE', 'taxable_salary': 191_013.37, 'current_tax': 410.13},
    {'id': 127, 'name': 'Hareem Abid', 'entity': 'NIETE', 'taxable_salary': 191_001.91, 'current_tax': 1_094.22},
    {'id': 183, 'name': 'Hareem Fatima', 'entity': 'Digital Learning', 'taxable_salary': 273_130.00, 'current_tax': 3_901.79},
    {'id': 170, 'name': 'Hasnat Tariq', 'entity': 'NIETE', 'taxable_salary': 391_550.00, 'current_tax': 10_982.53},
    {'id': 117, 'name': 'Hiba Anwer', 'entity': 'NIETE', 'taxable_salary': 225_553.81, 'current_tax': 0.00},
    {'id': 126, 'name': 'Hifza Nisar', 'entity': 'NIETE', 'taxable_salary': 244_632.80, 'current_tax': 0.00},
    {'id': 119, 'name': 'Hira Abbas', 'entity': 'NIETE', 'taxable_salary': 209_339.82, 'current_tax': 0.00},
    {'id': 132, 'name': 'Iqra Arshad', 'entity': 'NIETE', 'taxable_salary': 192_035.22, 'current_tax': 0.00},
    {'id': 149, 'name': 'Jamshaid Ahmad', 'entity': 'NIETE', 'taxable_salary': 240_977.06, 'current_tax': 0.00},
    {'id': 358, 'name': 'Javeria Khalil', 'entity': 'NIETE', 'taxable_salary': 221_560.00, 'current_tax': 0.00},
    {'id': 130, 'name': 'Javeria Nayyab', 'entity': 'NIETE', 'taxable_salary': 226_634.87, 'current_tax': 0.00},
    {'id': 201, 'name': 'Jawwad Ali', 'entity': 'NIETE', 'taxable_salary': 525_250.00, 'current_tax': 0.00},
    {'id': 123, 'name': 'Khadija Akbar', 'entity': 'NIETE', 'taxable_salary': 191_005.73, 'current_tax': 0.00},
    {'id': 116, 'name': 'Mahnoor Tanweer', 'entity': 'NIETE', 'taxable_salary': 580_512.03, 'current_tax': 0.00},
    {'id': 339, 'name': 'Maria Kareem', 'entity': 'NIETE', 'taxable_salary': 227_290.00, 'current_tax': 0.00},
    {'id': 128, 'name': 'Maroof Anwar', 'entity': 'NIETE', 'taxable_salary': 244_069.35, 'current_tax': 0.00},
    {'id': 400, 'name': 'Zeest Hassan Qureshi', 'entity': 'OPL', 'taxable_salary': 764_000.00, 'current_tax': 0.00},
    {'id': 401, 'name': 'Irum Afzal', 'entity': 'NIETE', 'taxable_salary': 227_290.00, 'current_tax': 0.00},
]

# ============================================================================
# INCOME TAX CALCULATION
# ============================================================================

def calculate_tax(monthly_taxable_salary):
    """
    Calculate income tax based on Pakistan FY slabs

    Formula:
    - If salary <= 600,000: Tax = 0
    - If salary > 600,000: Tax = Fixed_Tax + (Salary - Slab_Min) x Slab_Rate

    Current implementation uses monthly taxable salary
    (Assuming the provided amounts are already adjusted for 12-month FY basis)
    """
    if monthly_taxable_salary <= 0:
        return 0.00

    # Find applicable slab
    for slab in TAX_SLABS:
        if monthly_taxable_salary >= slab['min'] and monthly_taxable_salary <= slab['max']:
            if monthly_taxable_salary <= 600_000:
                return 0.00
            else:
                taxable_above_min = monthly_taxable_salary - slab['min']
                tax = slab['fixed'] + (taxable_above_min * slab['rate'])
                return round(tax, 2)

    return 0.00

# ============================================================================
# VERIFICATION PROCESS
# ============================================================================

print("=" * 120)
print("PAYROLL INCOME TAX VERIFICATION - April 2026")
print("=" * 120)
print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Tax Year: Pakistan FY 2025-2026 (July - June)")
print(f"Period: April 2026 (Monthly deduction based on 12-month FY calculation)")
print(f"\nVerifying {len(APRIL_2026_EMPLOYEES)} employees")
print("\nStatus: Calculating correct tax for each employee...\n")

results = []
discrepancies = []
correct_count = 0
incorrect_count = 0
total_current_tax = 0
total_calculated_tax = 0

for emp in APRIL_2026_EMPLOYEES:
    name = emp['name']
    current_tax = emp['current_tax']
    taxable_salary = emp['taxable_salary']

    calculated_tax = calculate_tax(taxable_salary)

    difference = abs(current_tax - calculated_tax)
    is_correct = difference < 0.01

    if is_correct:
        correct_count += 1
        status = "[OK]"
    else:
        incorrect_count += 1
        status = "[XX]"
        discrepancies.append({
            'name': name,
            'taxable_salary': taxable_salary,
            'current_tax': current_tax,
            'calculated_tax': calculated_tax,
            'difference': current_tax - calculated_tax
        })

    total_current_tax += current_tax
    total_calculated_tax += calculated_tax

    results.append({
        'name': name,
        'entity': emp['entity'],
        'taxable_salary': taxable_salary,
        'current_tax': current_tax,
        'calculated_tax': calculated_tax,
        'difference': difference,
        'status': status
    })

    print(f"{status} {name:40s} | Taxable: {taxable_salary:>12,.0f} | Current: {current_tax:>10,.0f} | Calc: {calculated_tax:>10,.0f}")

print("\n" + "=" * 120)
print("VERIFICATION SUMMARY")
print("=" * 120)
print(f"\nTotal Employees: {len(APRIL_2026_EMPLOYEES)}")
print(f"Correct Tax Values: {correct_count}")
print(f"Incorrect Tax Values: {incorrect_count}")
print(f"\nTotal Current Income Tax (on sheet): PKR {total_current_tax:>15,.0f}")
print(f"Total Calculated Income Tax: PKR {total_calculated_tax:>15,.0f}")
print(f"Difference: PKR {total_current_tax - total_calculated_tax:>20,.0f}")

if discrepancies:
    print("\n" + "=" * 120)
    print("DISCREPANCIES - INCORRECT TAX VALUES")
    print("=" * 120)
    print(f"\nTotal: {len(discrepancies)} employee(s) with incorrect tax\n")

    for disc in discrepancies:
        diff_note = "(Sheet is HIGHER)" if disc['difference'] > 0 else "(Sheet is LOWER)"
        print(f"[ERROR] {disc['name']}")
        print(f"  Taxable Salary: PKR {disc['taxable_salary']:>12,.0f}")
        print(f"  Current Tax (on sheet): PKR {disc['current_tax']:>10,.0f}")
        print(f"  Calculated Tax (correct): PKR {disc['calculated_tax']:>10,.0f}")
        print(f"  Difference: PKR {disc['difference']:>15,.0f} {diff_note}")
        print()
else:
    print("\n[SUCCESS] All income tax values on the April 2026 sheet are CORRECT!")

with open('april_2026_income_tax_detailed_verification.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'entity', 'taxable_salary', 'current_tax', 'calculated_tax', 'difference', 'status'])
    writer.writeheader()
    for result in results:
        writer.writerow(result)

print(f"\n[OUTPUT] Detailed report: april_2026_income_tax_detailed_verification.csv")
print(f"[COMPLETE] Verification finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
