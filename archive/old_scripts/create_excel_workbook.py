#!/usr/bin/env python3
"""Create Excel workbook with April 2026 tax calculations."""

import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pathlib import Path

# Read the CSV data
csv_file = r"C:\Agent Oreo\output\april_2026_tax_calculations.csv"
employees = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        employees.append(row)

print(f"Loaded {len(employees)} employees from CSV")

# Create workbook
wb = Workbook()

# ===== SHEET 1: EMPLOYEE TAX DATA =====
ws_data = wb.active
ws_data.title = "Employee Tax Data"

# Headers
headers = ['Employee Name', 'Type', 'April Taxable', 'YTD Through March',
           'Annual Taxable Projected', 'Annual Tax Liability',
           'Tax Collected Through March', 'April Income Tax']

ws_data.append(headers)

# Format header row
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF")
border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

for cell in ws_data[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.border = border
    cell.alignment = Alignment(horizontal='center', vertical='center')

# Add data rows
for emp in employees:
    try:
        row = [
            emp.get('Employee Name', ''),
            emp.get('Type', ''),
            float(emp.get('April Taxable', 0) or 0),
            float(emp.get('YTD Through March', 0) or 0),
            float(emp.get('Annual Taxable Projected', 0) or 0),
            float(emp.get('Annual Tax Liability', 0) or 0),
            float(emp.get('Tax Collected Through March', 0) or 0),
            float(emp.get('April Income Tax', 0) or 0)
        ]
        ws_data.append(row)
    except Exception as e:
        print(f"Error adding employee: {e}")

# Format number columns
for row in ws_data.iter_rows(min_row=2, max_row=len(employees)+1, min_col=3, max_col=8):
    for cell in row:
        cell.number_format = '#,##0'
        cell.alignment = Alignment(horizontal='right')
        cell.border = border

# Format text columns
for row in ws_data.iter_rows(min_row=2, max_row=len(employees)+1, min_col=1, max_col=2):
    for cell in row:
        cell.border = border
        cell.alignment = Alignment(horizontal='left')

# Set column widths
ws_data.column_dimensions['A'].width = 35
ws_data.column_dimensions['B'].width = 15
for col in ['C', 'D', 'E', 'F', 'G', 'H']:
    ws_data.column_dimensions[col].width = 18

# Freeze panes
ws_data.freeze_panes = 'A2'

# ===== SHEET 2: SUMMARY =====
ws_summary = wb.create_sheet("Summary")

total_april_tax = sum(float(e.get('April Income Tax', 0) or 0) for e in employees)
total_april_taxable = sum(float(e.get('April Taxable', 0) or 0) for e in employees)
existing_count = len([e for e in employees if e.get('Type') == 'Existing'])
new_joiner_count = len([e for e in employees if e.get('Type') == 'New Joiner'])
positive_tax = len([e for e in employees if float(e.get('April Income Tax', 0) or 0) > 0])
zero_tax = len([e for e in employees if float(e.get('April Income Tax', 0) or 0) == 0])

avg_tax_rate = (total_april_tax / total_april_taxable * 100) if total_april_taxable > 0 else 0

summary_data = [
    ['APRIL 2026 INCOME TAX CALCULATION - SUMMARY'],
    [],
    ['Metric', 'Value'],
    ['Total Employees', len(employees)],
    ['Existing Employees', existing_count],
    ['New Joiners', new_joiner_count],
    [],
    ['Total April Taxable Salary', total_april_taxable],
    ['Total April Income Tax', total_april_tax],
    ['Average Effective Tax Rate (%)', avg_tax_rate],
    [],
    ['Employees with Positive Tax', positive_tax],
    ['Employees with Zero Tax', zero_tax],
]

for row in summary_data:
    ws_summary.append(row)

# Format summary
title_cell = ws_summary['A1']
title_cell.font = Font(bold=True, size=14, color="FFFFFF")
title_cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

for row in ws_summary.iter_rows(min_row=3, max_row=13):
    if row[0].value:
        row[0].font = Font(bold=True)
        row[0].fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    if row[1].value is not None and isinstance(row[1].value, (int, float)):
        if isinstance(row[1].value, float) and row[1].value > 10:
            row[1].number_format = '#,##0.00'
        else:
            row[1].number_format = '#,##0.00'

ws_summary.column_dimensions['A'].width = 35
ws_summary.column_dimensions['B'].width = 20

# ===== SHEET 3: TOP 10 PAYERS =====
ws_top10 = wb.create_sheet("Top 10 Payers")

# Sort employees by April tax (descending)
sorted_emps = sorted(employees,
                     key=lambda x: float(x.get('April Income Tax', 0) or 0),
                     reverse=True)

ws_top10.append(['RANK', 'Employee Name', 'Employee Type', 'April Tax', 'Annual Tax Liability'])

for idx, emp in enumerate(sorted_emps[:10], 1):
    ws_top10.append([
        idx,
        emp.get('Employee Name', ''),
        emp.get('Type', ''),
        float(emp.get('April Income Tax', 0) or 0),
        float(emp.get('Annual Tax Liability', 0) or 0)
    ])

# Format Top 10 sheet
for cell in ws_top10[1]:
    cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    cell.font = Font(bold=True, color="FFFFFF")
    cell.border = border

for row in ws_top10.iter_rows(min_row=2, max_row=11):
    for idx, cell in enumerate(row):
        cell.border = border
        if idx == 0:
            cell.alignment = Alignment(horizontal='center')
        elif idx in [3, 4]:
            cell.number_format = '#,##0'
            cell.alignment = Alignment(horizontal='right')
        else:
            cell.alignment = Alignment(horizontal='left')

ws_top10.column_dimensions['A'].width = 6
ws_top10.column_dimensions['B'].width = 35
ws_top10.column_dimensions['C'].width = 15
ws_top10.column_dimensions['D'].width = 15
ws_top10.column_dimensions['E'].width = 18

# ===== SHEET 4: METHODOLOGY =====
ws_method = wb.create_sheet("Methodology")

methodology = [
    ['APRIL 2026 TAX CALCULATION METHODOLOGY'],
    [],
    ['FBR TAX SLABS (Pakistan 2025-26)'],
    ['Income Range', 'Tax Rate', 'Notes'],
    ['PKR 0 - 600,000', '0%', 'Exempt - No Tax'],
    ['PKR 600,000 - 1,200,000', '5%', 'First taxable slab'],
    ['PKR 1,200,000 - 1,800,000', '10%', ''],
    ['PKR 1,800,000 - 2,500,000', '15%', ''],
    ['PKR 2,500,000 - 3,200,000', '20%', ''],
    ['PKR 3,200,000 - 4,000,000', '25%', ''],
    ['Above PKR 4,000,000', '30%', 'Highest slab'],
    [],
    ['CALCULATION FORMULA'],
    ['Formula', 'Description'],
    ['CORRECT', 'April Tax = (Annual Tax Liability on 12-month projection) - (Tax Collected Jul-Mar)'],
    ['WRONG', 'April Tax = Annual Tax Liability ÷ 12 (DO NOT USE)'],
    [],
    ['STEPS FOR EXISTING EMPLOYEES:'],
    ['Step', 'Formula'],
    ['1. Calculate YTD', 'YTD = YTD(Jul-Feb) + Taxable Salary(March)'],
    ['2. Project Annual', 'Annual Taxable = YTD + April + (May) + (June)'],
    ['3. Annual Tax', 'Apply FBR progressive slab calculation'],
    ['4. April Tax', 'April Tax = Annual Tax - Tax Collected(Jul-Mar)'],
]

for row in methodology:
    ws_method.append(row)

title_cell = ws_method['A1']
title_cell.font = Font(bold=True, size=12, color="FFFFFF")
title_cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

ws_method.column_dimensions['A'].width = 35
ws_method.column_dimensions['B'].width = 60
ws_method.column_dimensions['C'].width = 30

# Save to Excel
output_path = r"C:\Agent Oreo\output\April_2026_Income_Tax_Calculations.xlsx"
wb.save(output_path)

print(f"\nExcel workbook created successfully!")
print(f"Location: {output_path}")
print(f"Total employees: {len(employees)}")
print(f"Sheets created:")
print(f"  1. Employee Tax Data (all {len(employees)} employees)")
print(f"  2. Summary (key metrics)")
print(f"  3. Top 10 Payers")
print(f"  4. Methodology (FBR slabs & formulas)")
