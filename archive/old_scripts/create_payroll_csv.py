#!/usr/bin/env python3
import json
import csv

# Load the calculated payroll data
with open('april_2026_payroll_final.json', 'r') as f:
    payroll_data = json.load(f)

# Create CSV for pasting into Google Sheets
csv_filename = 'april_2026_payroll_ready_to_paste.csv'

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        'emp_id', 'name', 'entity', 'gross_salary', 'basic_salary',
        'medical_allowance', 'other_allowance', 'unpaid_days', 'unpaid_days_amount',
        'commute_allowance', 'overtime', 'pending_dues', 'total_allowance',
        'taxable_salary', 'income_tax', 'abhi', 'advance', 'loan', 'buscaro',
        'lunch_meal', 'eobi', 'total_deductions', 'net_salary'
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for record in payroll_data:
        writer.writerow(record)

print(f"CSV created: {csv_filename}")
print(f"{len(payroll_data)} employees ready to paste")
total_net = sum(r['net_salary'] for r in payroll_data)
print(f"Total Net Payroll: PKR {total_net:,.0f}")

print("\nSheet Column Mapping (April 2026 payroll sheet):")
print("  Column L = Other Allowance")
print("  Column M = Unpaid Days Amount")
print("  Column N = Commute Allowance")
print("  Column O = Overtime")
print("  Column P = Pending Dues")
print("  Column Q = Total Allowance")
print("  Column R = Taxable Salary")
print("  Column S = Income Tax")
print("  Column T = ABHI")
print("  Column U = Advance")
print("  Column V = Loan")
print("  Column W = BusCaro")
print("  Column X = Lunch Meal")
print("  Column Y = EOBI")
print("  Column Z = Total Deductions")
print("  Column AA = Net Salary")
