#!/usr/bin/env python
"""
Analyze and format tax verification data into CSV files for easy comparison.
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def load_tax_data(json_file):
    """Load JSON data."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_comparison_csv(april_data, march_data, output_file):
    """Create a comparison CSV between April and March payroll."""

    # Create lookup dictionaries
    april_dict = {emp['Employee Name']: emp for emp in april_data}
    march_dict = {emp['Employee Name']: emp for emp in march_data}

    all_employees = sorted(set(list(april_dict.keys()) + list(march_dict.keys())))

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Headers
        writer.writerow([
            'Employee ID',
            'April 2026 - Taxable Salary',
            'April 2026 - Income Tax',
            'March 2026 - Taxable Salary',
            'March 2026 - Income Tax',
            'Salary Change',
            'Tax Change',
            'Status'
        ])

        april_total_taxable = 0
        april_total_tax = 0
        march_total_taxable = 0
        march_total_tax = 0

        # Data rows
        for emp_id in all_employees:
            april_emp = april_dict.get(emp_id, {})
            march_emp = march_dict.get(emp_id, {})

            april_tax = april_emp.get('Taxable Salary', '—')
            april_tax_amt = april_emp.get('Income Tax', '—')
            march_tax = march_emp.get('Taxable Salary', '—')
            march_tax_amt = march_emp.get('Income Tax', '—')

            # Try to parse numeric values
            try:
                april_val = float(april_tax.replace(',', '')) if april_tax != '—' else 0
                april_total_taxable += april_val
            except (ValueError, AttributeError):
                april_val = 0

            try:
                april_tax_val = float(april_tax_amt.replace(',', '')) if april_tax_amt != '—' else 0
                april_total_tax += april_tax_val
            except (ValueError, AttributeError):
                april_tax_val = 0

            try:
                march_val = float(march_tax.replace(',', '')) if march_tax != '—' else 0
                march_total_taxable += march_val
            except (ValueError, AttributeError):
                march_val = 0

            try:
                march_tax_val = float(march_tax_amt.replace(',', '')) if march_tax_amt != '—' else 0
                march_total_tax += march_tax_val
            except (ValueError, AttributeError):
                march_tax_val = 0

            # Calculate changes
            salary_change = april_val - march_val
            tax_change = april_tax_val - march_tax_val

            status = 'SAME' if salary_change == 0 else ('INCREASED' if salary_change > 0 else 'DECREASED')

            writer.writerow([
                emp_id,
                f"{april_val:,.2f}" if april_val else "—",
                f"{april_tax_val:,.2f}" if april_tax_val else "—",
                f"{march_val:,.2f}" if march_val else "—",
                f"{march_tax_val:,.2f}" if march_tax_val else "—",
                f"{salary_change:+,.2f}" if salary_change else "—",
                f"{tax_change:+,.2f}" if tax_change else "—",
                status
            ])

        # Totals row
        writer.writerow([])
        writer.writerow([
            'TOTAL',
            f"{april_total_taxable:,.2f}",
            f"{april_total_tax:,.2f}",
            f"{march_total_taxable:,.2f}",
            f"{march_total_tax:,.2f}",
            f"{april_total_taxable - march_total_taxable:+,.2f}",
            f"{april_total_tax - march_total_tax:+,.2f}",
            'COMPARISON'
        ])

def create_individual_csvs(data, prefix, output_dir='.'):
    """Create individual CSV for each payroll month."""

    output_file = Path(output_dir) / f'{prefix}_tax_verification.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Headers
        writer.writerow(['Employee ID', 'Taxable Salary', 'Income Tax', 'Net Tax Rate %'])

        total_taxable = 0
        total_tax = 0

        # Data rows
        for emp in data:
            emp_id = emp['Employee Name']
            taxable = emp['Taxable Salary']
            tax = emp['Income Tax']

            try:
                taxable_val = float(taxable.replace(',', '')) if taxable != '—' else 0
                total_taxable += taxable_val
            except (ValueError, AttributeError):
                taxable_val = 0

            try:
                tax_val = float(tax.replace(',', '')) if tax != '—' else 0
                total_tax += tax_val
            except (ValueError, AttributeError):
                tax_val = 0

            # Calculate tax rate
            tax_rate = (tax_val / taxable_val * 100) if taxable_val > 0 else 0

            writer.writerow([
                emp_id,
                f"{taxable_val:,.2f}" if taxable_val else "—",
                f"{tax_val:,.2f}" if tax_val else "—",
                f"{tax_rate:.2f}%" if tax_rate else "0.00%"
            ])

        # Summary row
        overall_rate = (total_tax / total_taxable * 100) if total_taxable > 0 else 0
        writer.writerow([])
        writer.writerow([
            'TOTAL',
            f"{total_taxable:,.2f}",
            f"{total_tax:,.2f}",
            f"{overall_rate:.2f}%"
        ])

    return output_file

def main():
    # Find the most recent JSON file
    json_files = sorted(Path('.').glob('tax_verification_data_*.json'), reverse=True)

    if not json_files:
        print("[ERROR] No tax verification data file found")
        return

    json_file = json_files[0]
    print(f"Loading data from: {json_file}\n")

    data = load_tax_data(json_file)

    if 'April 2026' not in data or 'March 2026' not in data:
        print("[ERROR] Missing required payroll data")
        return

    april_data = data['April 2026']
    march_data = data['March 2026']

    # Create comparison CSV
    print("[CREATING] April vs March Comparison...")
    comparison_file = 'tax_verification_comparison.csv'
    create_comparison_csv(april_data, march_data, comparison_file)
    print(f"[OK] Created: {comparison_file}\n")

    # Create individual CSVs
    print("[CREATING] Individual month CSVs...")
    april_file = create_individual_csvs(april_data, 'April_2026')
    print(f"[OK] Created: {april_file}")

    march_file = create_individual_csvs(march_data, 'March_2026')
    print(f"[OK] Created: {march_file}\n")

    # Print statistics
    print("="*80)
    print("TAX VERIFICATION SUMMARY")
    print("="*80 + "\n")

    print(f"APRIL 2026 PAYROLL:")
    print(f"  - Total Employees: {len(april_data)}")

    april_taxable_sum = 0
    april_tax_sum = 0
    april_non_zero = 0

    for emp in april_data:
        try:
            taxable = float(emp['Taxable Salary'].replace(',', '')) if emp['Taxable Salary'] != '—' else 0
            april_taxable_sum += taxable
        except (ValueError, AttributeError):
            pass

        try:
            tax = float(emp['Income Tax'].replace(',', '')) if emp['Income Tax'] != '—' else 0
            april_tax_sum += tax
            if tax > 0:
                april_non_zero += 1
        except (ValueError, AttributeError):
            pass

    print(f"  - Total Taxable Salary: {april_taxable_sum:,.2f}")
    print(f"  - Total Income Tax: {april_tax_sum:,.2f}")
    print(f"  - Overall Tax Rate: {(april_tax_sum/april_taxable_sum*100 if april_taxable_sum > 0 else 0):.2f}%")
    print(f"  - Employees with Tax > 0: {april_non_zero}\n")

    print(f"MARCH 2026 PAYROLL:")
    print(f"  - Total Employees: {len(march_data)}")

    march_taxable_sum = 0
    march_tax_sum = 0
    march_non_zero = 0

    for emp in march_data:
        try:
            taxable = float(emp['Taxable Salary'].replace(',', '')) if emp['Taxable Salary'] != '—' else 0
            march_taxable_sum += taxable
        except (ValueError, AttributeError):
            pass

        try:
            tax = float(emp['Income Tax'].replace(',', '')) if emp['Income Tax'] != '—' else 0
            march_tax_sum += tax
            if tax > 0:
                march_non_zero += 1
        except (ValueError, AttributeError):
            pass

    print(f"  - Total Taxable Salary: {march_taxable_sum:,.2f}")
    print(f"  - Total Income Tax: {march_tax_sum:,.2f}")
    print(f"  - Overall Tax Rate: {(march_tax_sum/march_taxable_sum*100 if march_taxable_sum > 0 else 0):.2f}%")
    print(f"  - Employees with Tax > 0: {march_non_zero}\n")

    print("TAX WORKING SHEET (Slabs for 2025-2026):")
    if 'Tax Working Sheet' in data:
        tax_sheet = data['Tax Working Sheet']
        print(f"  - Total Rows: {len(tax_sheet)}")
        print(f"  - Contains 6 tax slabs + 1 BTL category\n")

if __name__ == '__main__':
    main()
