#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculate April 2026 Income Tax based on 9-month history
Annual tax projection method
"""

import json
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print('=' * 120)
print('CALCULATING APRIL 2026 INCOME TAX')
print('Financial Year Method: Jul 2025 - Jun 2026')
print('=' * 120)
print()

# Load 9-month tax database
try:
    with open('tax_history_9months.json', 'r') as f:
        tax_database = json.load(f)
except FileNotFoundError:
    print('ERROR: tax_history_9months.json not found')
    sys.exit(1)

print(f'Loaded 9-month tax history for {len(tax_database)} employees')
print()

# Calculate April tax for each employee
april_tax_calculations = {}

print('CALCULATING ANNUAL TAX PROJECTIONS')
print('-' * 120)
print()

for emp_idx, (name_lower, months_data) in enumerate(tax_database.items(), 1):
    # Get employee name from any month's data
    emp_name = None
    months_with_data = []
    total_tax_9m = 0
    average_gross = 0

    for month, month_data in months_data.items():
        emp_name = month_data.get('name', name_lower)
        months_with_data.append(month)
        total_tax_9m += month_data.get('tax', 0)
        average_gross += month_data.get('gross', 0)

    if len(months_with_data) == 0:
        continue

    # Calculate averages and projections
    num_months = len(months_with_data)
    average_gross = average_gross / num_months if num_months > 0 else 0
    average_monthly_tax = total_tax_9m / num_months if num_months > 0 else 0

    # Annual projection (only for employees present in all 9 months)
    if num_months == 9:
        # Full 9 months of data - use this to project annual
        # Assumption: monthly salary stable throughout year
        projected_annual_tax = (total_tax_9m / 9) * 12
        remaining_tax = projected_annual_tax - total_tax_9m
        april_tax = remaining_tax / 3  # 3 remaining months (Apr, May, Jun)
    else:
        # Partial year - estimate based on available months
        projected_annual_tax = (total_tax_9m / num_months) * 12
        remaining_tax = projected_annual_tax - total_tax_9m
        april_tax = remaining_tax / 3

    # Store calculation
    april_tax_calculations[name_lower] = {
        'name': emp_name,
        'months_active': num_months,
        'average_gross': round(average_gross, 2),
        'total_tax_9m': round(total_tax_9m, 2),
        'average_monthly_tax': round(average_monthly_tax, 2),
        'projected_annual_tax': round(projected_annual_tax, 2),
        'remaining_tax': round(remaining_tax, 2),
        'april_tax': round(april_tax, 2)
    }

    # Show sample data
    if emp_idx <= 10:
        clean_name = emp_name.encode('utf-8', errors='ignore').decode('utf-8')
        print(f'{emp_idx}. {clean_name}')
        print(f'   Months active: {num_months}/9')
        print(f'   Avg gross/month: {average_gross:10.0f}')
        print(f'   Tax deducted (9 months): {total_tax_9m:10.0f}')
        print(f'   Projected annual tax: {projected_annual_tax:10.0f}')
        print(f'   Remaining tax (Apr-Jun): {remaining_tax:10.0f}')
        print(f'   April 2026 tax: {april_tax:10.0f}')
        print()

print('=' * 120)
print('SUMMARY OF CALCULATIONS')
print('=' * 120)
print()

# Calculate statistics
total_april_tax = sum(calc.get('april_tax', 0) for calc in april_tax_calculations.values())
employees_with_april_tax = sum(1 for calc in april_tax_calculations.values() if calc.get('april_tax', 0) > 0)
employees_zero_tax = sum(1 for calc in april_tax_calculations.values() if calc.get('april_tax', 0) == 0)

print(f'Total employees analyzed: {len(april_tax_calculations)}')
print(f'Employees with April tax: {employees_with_april_tax}')
print(f'Employees with zero tax: {employees_zero_tax}')
print()
print(f'Total income tax to deduct in April 2026: {total_april_tax:,.2f} PKR')
print()

print('=' * 120)
print('SAVING APRIL TAX CALCULATIONS')
print('=' * 120)
print()

# Save to file
with open('april_2026_tax_calculated.json', 'w') as f:
    json.dump(april_tax_calculations, f, indent=2)

print('[OK] Saved to: april_2026_tax_calculated.json')
print()
print('Next step: Apply these tax amounts to April 2026 payroll sheet')
print()
