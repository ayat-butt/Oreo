#!/usr/bin/env python3
"""
Comprehensive OPL Joiners and Leavers Audit
July 2024 - June 2025
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from datetime import datetime

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error: {e}")
        return None

def fetch_sheet_data(service, sheet_id, sheet_name, tab_name='OPL'):
    """Fetch OPL data from a specific sheet tab"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab_name}'!A1:Z500"
        ).execute()
        return result.get('values', [])
    except HttpError as e:
        if 'INVALID_ARGUMENT' in str(e) or 'not found' in str(e).lower():
            return []
        raise

def extract_opl_employees(rows):
    """Extract OPL employee list from payroll data"""
    employees = {}

    if not rows or len(rows) < 2:
        return employees

    # Find header row
    header_row = None
    for i, row in enumerate(rows[:5]):
        if row and len(row) > 1 and 'Employee' in str(row[1]):
            header_row = i
            break

    if header_row is None:
        return employees

    headers = rows[header_row]
    name_col = None
    dept_col = None
    gross_sal_col = None

    for col_idx, header in enumerate(headers):
        header_str = str(header).lower()
        if 'employee' in header_str and name_col is None:
            name_col = col_idx
        elif 'department' in header_str:
            dept_col = col_idx
        elif 'gross' in header_str and 'salary' in header_str:
            gross_sal_col = col_idx

    # Extract employee data
    for row_idx in range(header_row + 1, len(rows)):
        row = rows[row_idx]
        if not row or len(row) < 2:
            continue

        name = row[name_col].strip() if name_col and name_col < len(row) else None
        if not name or name == '':
            continue

        dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
        salary = row[gross_sal_col].strip() if gross_sal_col and gross_sal_col < len(row) else ''

        # Skip if obviously a total row
        if 'total' in name.lower() or 'sum' in name.lower():
            continue

        employees[name] = {
            'name': name,
            'department': dept,
            'salary': salary
        }

    return employees

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    # Define sheets to process
    sheets_to_process = [
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'July, 2024', 'July 2024'),
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'August 2024', 'August 2024'),
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'September 2024', 'September 2024'),
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'October 2024', 'October 2024'),
        ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL', 'November 2024'),
        ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL', 'December 2024'),
        ('1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL', 'January 2025'),
        ('1T5rMIo0Apv41Tm-jDstU1qT5Lp6raFGhBNaYPIR4oe0', 'OPL', 'February 2025'),
        ('17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc', 'OPL', 'March 2025'),
        ('1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k', 'OPL', 'April 2025'),
        ('1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0', 'OPL', 'May 2025'),
        ('1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us', 'OPL', 'June 2025'),
    ]

    monthly_data = {}

    print("="*100)
    print("OPL AUDIT: EXTRACTING EMPLOYEE DATA (July 2024 - June 2025)")
    print("="*100)

    for sheet_id, tab_name, month_label in sheets_to_process:
        try:
            print(f"\nFetching {month_label}...", end=' ')
            rows = fetch_sheet_data(service, sheet_id, sheet_id, tab_name)
            employees = extract_opl_employees(rows)
            monthly_data[month_label] = employees
            print(f"Found {len(employees)} employees")
        except Exception as e:
            print(f"ERROR: {e}")
            monthly_data[month_label] = {}

    # Analyze joiners and leavers
    print("\n" + "="*100)
    print("ANALYSIS: JOINERS AND LEAVERS")
    print("="*100)

    all_joiners = {}
    all_leavers = {}
    all_employees = set()

    # Get all unique employee names across all months
    for month, employees in monthly_data.items():
        all_employees.update(employees.keys())

    months_list = list(monthly_data.keys())

    # Compare consecutive months
    for i in range(len(months_list) - 1):
        current_month = months_list[i]
        next_month = months_list[i + 1]

        current_employees = set(monthly_data[current_month].keys())
        next_employees = set(monthly_data[next_month].keys())

        # Joiners: in next month but not in current
        joiners = next_employees - current_employees
        for name in joiners:
            if name not in all_joiners:
                all_joiners[name] = {
                    'name': name,
                    'joining_month': next_month,
                    'joining_date': next_month,
                    'data': monthly_data[next_month][name]
                }

        # Leavers: in current month but not in next
        leavers = current_employees - next_employees
        for name in leavers:
            if name not in all_leavers:
                all_leavers[name] = {
                    'name': name,
                    'leaving_month': next_month,
                    'leaving_date': next_month,
                    'data': monthly_data[current_month][name]
                }

    # Print results
    print(f"\nJOINERS ({len(all_joiners)} total)")
    print("-"*100)
    for name, info in sorted(all_joiners.items()):
        print(f"  {name:<40} | Joined: {info['joining_month']:<15} | Dept: {info['data']['department']:<30} | Salary: {info['data']['salary']}")

    print(f"\nLEAVERS ({len(all_leavers)} total)")
    print("-"*100)
    for name, info in sorted(all_leavers.items()):
        print(f"  {name:<40} | Left: {info['leaving_month']:<15} | Dept: {info['data']['department']:<30} | Salary: {info['data']['salary']}")

    # Save results
    output_file = 'output/OPL_Joiners_Leavers_Audit_Jul2024_Jun2025.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*100 + "\n")
        f.write("OPL AUDIT: JOINERS AND LEAVERS (July 2024 - June 2025)\n")
        f.write("="*100 + "\n\n")

        f.write(f"JOINERS ({len(all_joiners)} total)\n")
        f.write("-"*100 + "\n")
        for name, info in sorted(all_joiners.items()):
            f.write(f"{name:<40} | Joined: {info['joining_month']:<15} | Dept: {info['data']['department']:<30} | Salary: {info['data']['salary']}\n")

        f.write(f"\nLEAVERS ({len(all_leavers)} total)\n")
        f.write("-"*100 + "\n")
        for name, info in sorted(all_leavers.items()):
            f.write(f"{name:<40} | Left: {info['leaving_month']:<15} | Dept: {info['data']['department']:<30} | Salary: {info['data']['salary']}\n")

        f.write(f"\nSUMMARY\n")
        f.write("-"*100 + "\n")
        f.write(f"Total Joiners: {len(all_joiners)}\n")
        f.write(f"Total Leavers: {len(all_leavers)}\n")
        f.write(f"Net Change: {len(all_joiners) - len(all_leavers)}\n")

    print(f"\n[DONE] Report saved to: {output_file}")
    print(f"\nSUMMARY")
    print("-"*100)
    print(f"Total Joiners: {len(all_joiners)}")
    print(f"Total Leavers: {len(all_leavers)}")
    print(f"Net Change: {len(all_joiners) - len(all_leavers)}")

if __name__ == '__main__':
    main()
