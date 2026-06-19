#!/usr/bin/env python3
"""Complete OPL Month-by-Month Audit from July 2024 - June 2025"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

def fetch_payroll_data(service, sheet_id, sheet_name):
    """Fetch payroll data from sheet"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A1:Z500"
        ).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"  Error fetching {sheet_name}: {e}")
        return []

def extract_opl_employees(rows):
    """Extract OPL employee names and details"""
    employees = {}

    if not rows or len(rows) < 2:
        return employees

    # Find header row
    header_row = None
    for i, row in enumerate(rows[:10]):
        if row and any('employee' in str(cell).lower() for cell in row):
            header_row = i
            break

    if header_row is None:
        return employees

    headers = rows[header_row]
    name_col = None
    dept_col = None
    salary_col = None
    designation_col = None

    # Map columns
    for col_idx, header in enumerate(headers):
        h = str(header).lower()
        if 'employee' in h and name_col is None:
            name_col = col_idx
        elif 'depart' in h:
            dept_col = col_idx
        elif 'gross' in h and 'salary' in h:
            salary_col = col_idx
        elif 'designation' in h or 'title' in h:
            designation_col = col_idx

    # Extract employee data
    for row_idx in range(header_row + 1, len(rows)):
        row = rows[row_idx]
        if not row or len(row) < 2:
            continue

        name = row[name_col].strip() if name_col and name_col < len(row) else ''
        if not name or name == '' or name.isdigit() or 'total' in name.lower():
            continue
        if len(name) < 3 or not any(c.isalpha() for c in name):
            continue

        dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
        salary = row[salary_col].strip() if salary_col and salary_col < len(row) else ''
        designation = row[designation_col].strip() if designation_col and designation_col < len(row) else ''

        employees[name] = {
            'name': name,
            'department': dept,
            'salary': salary,
            'designation': designation
        }

    return employees

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    # Complete list with corrected July-October links
    monthly_sheets = {
        'July 2024': ('1tIKIU0LKCR2YYuCS0u0lb_Gr-rDm6ks_', 'OPL'),
        'August 2024': ('15n2DllSdSDErWwl0pj3PkeqwJKF5LDbZ', 'OPL'),
        'September 2024': ('1bP1Ju0vzcS7QxF1NkheVZpI6HxliE-F7', 'OPL'),
        'October 2024': ('1h1IRXwxx-mRAp0m2C2sqHlIjR5OzYpjc', 'OPL'),
        'November 2024': ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL'),
        'December 2024': ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL'),
        'January 2025': ('1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL'),
        'February 2025': ('1T5rMIo0Apv41Tm-jDstU1qT5Lp6raFGhBNaYPIR4oe0', 'OPL'),
        'March 2025': ('17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc', 'OPL'),
        'April 2025': ('1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k', 'OPL'),
        'May 2025': ('1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0', 'OPL'),
        'June 2025': ('1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us', 'OPL'),
    }

    # Track employees by month
    monthly_employees = {}

    print("="*120)
    print("COMPLETE OPL MONTH-BY-MONTH AUDIT: JULY 2024 - JUNE 2025")
    print("="*120)
    print("\nFetching payroll data from each month...\n")

    months_ordered = ['July 2024', 'August 2024', 'September 2024', 'October 2024',
                      'November 2024', 'December 2024', 'January 2025', 'February 2025',
                      'March 2025', 'April 2025', 'May 2025', 'June 2025']

    for month_label in months_ordered:
        if month_label in monthly_sheets:
            sheet_id, tab_name = monthly_sheets[month_label]
            print(f"Processing {month_label}...", end=' ')

            rows = fetch_payroll_data(service, sheet_id, tab_name)
            employees = extract_opl_employees(rows)
            monthly_employees[month_label] = employees

            print(f"Found {len(employees)} OPL employees")
        else:
            print(f"Skipping {month_label} - not in list")

    # Analyze month-by-month changes
    print("\n" + "="*120)
    print("MONTH-BY-MONTH ANALYSIS: JOINERS AND LEAVERS")
    print("="*120)

    all_joiners = {}
    all_leavers = {}

    # Track opening balance
    july_employees = monthly_employees.get('July 2024', {})
    print(f"\nOPENING BALANCE (July 2024): {len(july_employees)} employees")

    # Compare consecutive months
    for i in range(len(months_ordered) - 1):
        current_month = months_ordered[i]
        next_month = months_ordered[i + 1]

        current_employees = set(monthly_employees[current_month].keys())
        next_employees = set(monthly_employees[next_month].keys())

        # New joiners: in next month but not in current
        joiners = next_employees - current_employees
        if joiners:
            print(f"\n[JOINERS] Between {current_month} and {next_month}: {len(joiners)} new employees")
            for name in sorted(joiners):
                emp = monthly_employees[next_month][name]
                print(f"  + {name:<40} | Dept: {emp['department']:<40} | Salary: {emp['salary']}")

                if name not in all_joiners:
                    all_joiners[name] = {
                        'name': name,
                        'joining_month': next_month,
                        'department': emp['department'],
                        'designation': emp['designation'],
                        'salary': emp['salary']
                    }

        # Leavers: in current month but not in next
        leavers = current_employees - next_employees
        if leavers:
            print(f"\n[LEAVERS] Between {current_month} and {next_month}: {len(leavers)} employees left")
            for name in sorted(leavers):
                emp = monthly_employees[current_month][name]
                print(f"  - {name:<40} | Dept: {emp['department']:<40} | Salary: {emp['salary']}")

                if name not in all_leavers:
                    all_leavers[name] = {
                        'name': name,
                        'leaving_month': next_month,
                        'department': emp['department'],
                        'designation': emp['designation'],
                        'salary': emp['salary']
                    }

    # Summary
    print("\n" + "="*120)
    print("FINAL SUMMARY REPORT")
    print("="*120)

    print(f"\nOpening Balance (July 2024): {len(july_employees)} employees")
    print(f"Total New Joiners (July 2024 - June 2025): {len(all_joiners)}")
    print(f"Total Employees Who Left (July 2024 - June 2025): {len(all_leavers)}")

    # Save detailed report
    output_file = 'output/OPL_COMPLETE_MONTHWISE_AUDIT.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*120 + "\n")
        f.write("COMPLETE OPL MONTH-BY-MONTH AUDIT: JULY 2024 - JUNE 2025\n")
        f.write("="*120 + "\n\n")

        f.write(f"OPENING BALANCE (July 2024): {len(july_employees)} employees\n")
        f.write("-"*120 + "\n")
        for name in sorted(july_employees.keys()):
            emp = july_employees[name]
            f.write(f"{name:<40} | Dept: {emp['department']:<40} | Salary: {emp['salary']}\n")

        f.write(f"\n\nNEW JOINERS (After July 2024): {len(all_joiners)} employees\n")
        f.write("-"*120 + "\n")
        for name in sorted(all_joiners.keys()):
            joiner = all_joiners[name]
            f.write(f"{name:<40} | Joined: {joiner['joining_month']:<15} | Dept: {joiner['department']:<40}\n")

        f.write(f"\n\nEMPLOYEES WHO LEFT: {len(all_leavers)} employees\n")
        f.write("-"*120 + "\n")
        for name in sorted(all_leavers.keys()):
            leaver = all_leavers[name]
            f.write(f"{name:<40} | Left: {leaver['leaving_month']:<15} | Dept: {leaver['department']:<40}\n")

    print(f"\nDetailed report saved to: {output_file}")

if __name__ == '__main__':
    main()
