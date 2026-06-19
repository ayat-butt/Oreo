#!/usr/bin/env python3
"""
PAYROLL INCOME TAX VERIFICATION & CALCULATION — April 2026
Pakistan FY Tax Calculation (Jul-Jun)
Verify current April sheet tax values and show correct calculations
"""

import csv
from datetime import datetime

# ============================================================================
# MARCH 2026 TAX DATA (Source: Tax Working Sheet)
# ============================================================================

MARCH_2026_TAX_DATA = {
    'Anam Masood': {'annual_tax': 234_014, 'tax_jul_feb': 156_009, 'mar_tax': 19_501.32},
    'Aneela Khaliq': {'annual_tax': 21_736, 'tax_jul_feb': 19_733, 'mar_tax': 500.52},
    'Aown Raza': {'annual_tax': 0, 'tax_jul_feb': 0, 'mar_tax': 0},
    'Areej Noshad': {'annual_tax': 18_326, 'tax_jul_feb': 13_243, 'mar_tax': 1_270.52},
    'Ashas Khan': {'annual_tax': 33_036, 'tax_jul_feb': 28_697, 'mar_tax': 1_084.91},
    'Asma Zaheer': {'annual_tax': 146_008, 'tax_jul_feb': 83_457, 'mar_tax': 15_637.72},
    'Ayat Butt': {'annual_tax': 5_484, 'tax_jul_feb': 3_661, 'mar_tax': 455.55},
    'Bushra': {'annual_tax': 48_390, 'tax_jul_feb': 35_231, 'mar_tax': 3_289.95},
    'Chaudhary Hashir Hussain Shahid': {'annual_tax': 89_639, 'tax_jul_feb': 52_813, 'mar_tax': 9_206.51},
    'Danish Iqbal': {'annual_tax': 31_013, 'tax_jul_feb': 21_635, 'mar_tax': 2_344.56},
    'Eysha Qadeer': {'annual_tax': 15_904, 'tax_jul_feb': 11_526, 'mar_tax': 1_094.41},
    'Hafiz Abdul Malik': {'annual_tax': 38_759, 'tax_jul_feb': 33_184, 'mar_tax': 1_393.82},
    'Hafsa Bashir': {'annual_tax': 20_014, 'tax_jul_feb': 13_313, 'mar_tax': 1_675.39},
    'Hamza Razaq': {'annual_tax': 0, 'tax_jul_feb': 0, 'mar_tax': 0},
    'Hamza Shahid': {'annual_tax': 234_009, 'tax_jul_feb': 157_565, 'mar_tax': 20_911},
    'Hamza Siddique': {'annual_tax': 4_921, 'tax_jul_feb': 3_280, 'mar_tax': 410.13},
    'Hareem Abid': {'annual_tax': 15_901, 'tax_jul_feb': 11_524, 'mar_tax': 1_094.22},
    'Hareem Fatima': {'annual_tax': 33_672, 'tax_jul_feb': 18_065, 'mar_tax': 3_901.79},
    'Hasnat Tariq': {'annual_tax': 131_165, 'tax_jul_feb': 87_234, 'mar_tax': 10_982.53},
    'Hiba Anwer': {'annual_tax': 33_341, 'tax_jul_feb': 21_556, 'mar_tax': 2_946.22},
    'Hifza Nisar': {'annual_tax': 53_678, 'tax_jul_feb': 36_721, 'mar_tax': 4_239.23},
    'Hira Abbas': {'annual_tax': 5_969, 'tax_jul_feb': 3_979, 'mar_tax': 497.44},
    'Iqra Arshad': {'annual_tax': 5_017, 'tax_jul_feb': 3_358, 'mar_tax': 414.94},
    'Jamshaid Ahmad': {'annual_tax': 54_481, 'tax_jul_feb': 38_208, 'mar_tax': 4_068.06},
    'Javeria Nayyab': {'annual_tax': 45_461, 'tax_jul_feb': 32_195, 'mar_tax': 3_316.47},
    'Jawwad Ali': {'annual_tax': 294_661, 'tax_jul_feb': 196_774, 'mar_tax': 32_640},
    'Khadija Akbar': {'annual_tax': 9_964, 'tax_jul_feb': 5_454, 'mar_tax': 1_127.37},
    'Mahnoor Tanweer': {'annual_tax': 381_684, 'tax_jul_feb': 254_456, 'mar_tax': 31_806.99},
    'Maria Kareem': {'annual_tax': 10_820, 'tax_jul_feb': 7_213, 'mar_tax': 1_202},
    'Maroof Anwar': {'annual_tax': 43_115, 'tax_jul_feb': 29_109, 'mar_tax': 3_501.47},
    'Zeest Hassan Qureshi': {'annual_tax': 0, 'tax_jul_feb': 0, 'mar_tax': 0},  # New joiner - no historical data
    'Irum Afzal': {'annual_tax': 0, 'tax_jul_feb': 0, 'mar_tax': 0},  # New joiner - no historical data
}

# ============================================================================
# APRIL 2026 EMPLOYEES WITH CURRENT TAX VALUES (From April Sheet)
# ============================================================================

APRIL_2026_EMPLOYEES = [
    {'name': 'Abdul Waheed', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Aleeha Noor', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Anam Masood', 'entity': 'NIETE', 'current_tax': 19_501.32},
    {'name': 'Aneela Khaliq', 'entity': 'NIETE', 'current_tax': 500.52},
    {'name': 'Aown Raza', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Areej Noshad', 'entity': 'NIETE', 'current_tax': 1_270.52},
    {'name': 'Ashas Khan', 'entity': 'NIETE', 'current_tax': 1_084.91},
    {'name': 'Asma Zaheer', 'entity': 'NIETE', 'current_tax': 15_637.72},
    {'name': 'Ayat Butt', 'entity': 'NIETE', 'current_tax': 455.55},
    {'name': 'Bushra', 'entity': 'NIETE', 'current_tax': 3_289.95},
    {'name': 'Chaudhary Hashir Hussain Shahid', 'entity': 'NIETE', 'current_tax': 9_206.51},
    {'name': 'Danish Iqbal', 'entity': 'NIETE', 'current_tax': 2_344.56},
    {'name': 'Eysha Qadeer', 'entity': 'NIETE', 'current_tax': 1_094.41},
    {'name': 'Hafiz Abdul Malik', 'entity': 'NIETE', 'current_tax': 1_393.82},
    {'name': 'Hafsa Bashir', 'entity': 'Digital Learning', 'current_tax': 1_675.39},
    {'name': 'Hamza Razaq', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Hamza Shahid', 'entity': 'OWT', 'current_tax': 5_584.18},
    {'name': 'Hamza Siddique', 'entity': 'NIETE', 'current_tax': 410.13},
    {'name': 'Hareem Abid', 'entity': 'NIETE', 'current_tax': 1_094.22},
    {'name': 'Hareem Fatima', 'entity': 'Digital Learning', 'current_tax': 3_901.79},
    {'name': 'Hasnat Tariq', 'entity': 'NIETE', 'current_tax': 10_982.53},
    {'name': 'Hiba Anwer', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Hifza Nisar', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Hira Abbas', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Iqra Arshad', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Jamshaid Ahmad', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Javeria Khalil', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Javeria Nayyab', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Jawwad Ali', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Khadija Akbar', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Mahnoor Tanweer', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Maria Kareem', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Maroof Anwar', 'entity': 'NIETE', 'current_tax': 0.00},
    {'name': 'Zeest Hassan Qureshi', 'entity': 'OPL', 'current_tax': 0.00},
    {'name': 'Irum Afzal', 'entity': 'NIETE', 'current_tax': 0.00},
]

# ============================================================================
# INCOME TAX CALCULATION
# ============================================================================

def calculate_april_tax(employee_name):
    """
    Calculate April 2026 Income Tax using FY formula:
    April Tax = (Annual Tax Liability - Tax Collected Jul-Mar) / 3
    """
    if employee_name not in MARCH_2026_TAX_DATA:
        # New joiners or employees without tax history
        return 0.00

    data = MARCH_2026_TAX_DATA[employee_name]
    annual_tax = data['annual_tax']
    tax_collected = data['tax_jul_feb'] + data['mar_tax']

    if annual_tax == 0 or annual_tax is None:
        return 0.00

    remaining_tax = annual_tax - tax_collected
    april_tax = remaining_tax / 3

    return round(april_tax, 2)

# ============================================================================
# VERIFICATION PROCESS
# ============================================================================

print("=" * 140)
print("PAYROLL INCOME TAX VERIFICATION & CALCULATION — APRIL 2026")
print("=" * 140)
print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Tax Year: Pakistan FY 2025-2026 (July 2025 - June 2026)")
print(f"\nFormula: April 2026 Tax = (Annual Tax Liability - Tax Collected Jul-Mar) / 3")
print(f"         Where Tax Collected Jul-Mar = Tax Jul-Feb + March Tax")
print(f"\nVerifying {len(APRIL_2026_EMPLOYEES)} employees\n")

results = []
entity_summary = {}
correct_count = 0
incorrect_count = 0
total_current_tax = 0
total_calculated_tax = 0

for emp in APRIL_2026_EMPLOYEES:
    name = emp['name']
    entity = emp['entity']
    current_tax = emp['current_tax']

    calculated_tax = calculate_april_tax(name)

    difference = abs(current_tax - calculated_tax)
    is_correct = difference < 0.01

    if is_correct:
        correct_count += 1
        status = "[OK]"
    else:
        incorrect_count += 1
        status = "[XX]"

    total_current_tax += current_tax
    total_calculated_tax += calculated_tax

    # Entity summary
    if entity not in entity_summary:
        entity_summary[entity] = {'count': 0, 'current': 0, 'calculated': 0, 'correct': 0}
    entity_summary[entity]['count'] += 1
    entity_summary[entity]['current'] += current_tax
    entity_summary[entity]['calculated'] += calculated_tax
    if is_correct:
        entity_summary[entity]['correct'] += 1

    results.append({
        'name': name,
        'entity': entity,
        'current_tax': current_tax,
        'calculated_tax': calculated_tax,
        'difference': difference,
        'status': status
    })

    print(f"{status} {name:40s} | {entity:18s} | Current: {current_tax:>10,.2f} | Calc: {calculated_tax:>10,.2f}")

print("\n" + "=" * 140)
print("VERIFICATION SUMMARY BY ENTITY")
print("=" * 140)

for entity in sorted(entity_summary.keys()):
    summary = entity_summary[entity]
    print(f"\n{entity}:")
    print(f"  Employees: {summary['count']} | Correct: {summary['correct']} | Incorrect: {summary['count'] - summary['correct']}")
    print(f"  Current Tax Total: PKR {summary['current']:>15,.2f}")
    print(f"  Calculated Tax Total: PKR {summary['calculated']:>15,.2f}")
    print(f"  Difference: PKR {summary['current'] - summary['calculated']:>20,.2f}")

print("\n" + "=" * 140)
print("OVERALL SUMMARY")
print("=" * 140)
print(f"\nTotal Employees: {len(APRIL_2026_EMPLOYEES)}")
print(f"Correct Tax Values: {correct_count}")
print(f"Incorrect Tax Values: {incorrect_count}")
print(f"\nTotal Current Income Tax (on April sheet): PKR {total_current_tax:>15,.2f}")
print(f"Total Calculated Income Tax (correct): PKR {total_calculated_tax:>15,.2f}")
print(f"Difference: PKR {total_current_tax - total_calculated_tax:>20,.2f}")

if incorrect_count > 0:
    print(f"\n[ALERT] {incorrect_count} employee(s) have DISCREPANCIES")
    discrepancies = [r for r in results if r['status'] == "[XX]"]
    print(f"\nDISCREPANCIES FOUND:\n")
    for disc in discrepancies:
        print(f"[ERROR] {disc['name']:40s} | {disc['entity']:18s}")
        print(f"        Current: PKR {disc['current_tax']:>10,.2f} | Calculated: PKR {disc['calculated_tax']:>10,.2f} | Diff: PKR {disc['difference']:>10,.2f}")
else:
    print(f"\n[SUCCESS] All {correct_count} employees have CORRECT income tax values!")

# Save detailed report
with open('april_2026_income_tax_final_verification.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'entity', 'current_tax', 'calculated_tax', 'difference', 'status'])
    writer.writeheader()
    for result in results:
        writer.writerow(result)

print(f"\n[OUTPUT] Detailed report: april_2026_income_tax_final_verification.csv")
print(f"[COMPLETE] Verification finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n[PAYROLL NOTE] All calculations based on March 2026 Tax Working Sheet (FY Jul-Jun basis)")
print(f"[PAYROLL NOTE] New joiners (Zeest Hassan Qureshi, Irum Afzal) calculated at 0 until historical data available")
