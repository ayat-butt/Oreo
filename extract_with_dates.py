#!/usr/bin/env python3
"""
Extract OPL employees with specific joining and leaving dates
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
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
    except:
        return None

def fetch_sheet_data(service, sheet_id, tab_name):
    """Fetch data from sheet"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab_name}'!A1:Z500"
        ).execute()
        return result.get('values', [])
    except:
        return []

def extract_employees_with_dates(rows):
    """Extract employee data including joining dates from payroll"""
    employees = {}

    if not rows or len(rows) < 2:
        return employees

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
    gross_sal_col = None
    designation_col = None

    for col_idx, header in enumerate(headers):
        h = str(header).lower()
        if 'employee' in h and name_col is None:
            name_col = col_idx
        elif 'depart' in h:
            dept_col = col_idx
        elif 'gross' in h and 'salary' in h:
            gross_sal_col = col_idx
        elif 'designation' in h or 'title' in h:
            designation_col = col_idx

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
        salary = row[gross_sal_col].strip() if gross_sal_col and gross_sal_col < len(row) else ''
        designation = row[designation_col].strip() if designation_col and designation_col < len(row) else ''

        employees[name] = {
            'name': name,
            'department': dept,
            'salary': salary,
            'designation': designation,
            'joining_date': '',
            'leaving_date': ''
        }

    return employees

def extract_addition_deletion_dates(rows):
    """Extract joining/leaving dates from addition/deletion sheet"""
    dates = {}

    if not rows or len(rows) < 2:
        return dates

    # Find sections
    for i, row in enumerate(rows):
        if row and 'employee' in str(row[0]).lower() and 'addition' in str(row[0]).lower():
            # Addition section found at row i
            header_row = i + 1
            if header_row < len(rows):
                headers = rows[header_row]
                name_col = None
                date_col = None

                for col_idx, header in enumerate(headers):
                    h = str(header).lower()
                    if 'name' in h:
                        name_col = col_idx
                    if 'join' in h and 'date' in h:
                        date_col = col_idx

                # Extract data
                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if not row or len(row) < 2 or not row[0].strip():
                        continue

                    name = row[name_col].strip() if name_col and name_col < len(row) else ''
                    join_date = row[date_col].strip() if date_col and date_col < len(row) else ''

                    if name and join_date:
                        dates[name] = {
                            'joining_date': join_date,
                            'leaving_date': ''
                        }

        elif row and 'employee' in str(row[0]).lower() and 'separat' in str(row[0]).lower():
            # Separation section
            header_row = i + 1
            if header_row < len(rows):
                headers = rows[header_row]
                name_col = None
                date_col = None

                for col_idx, header in enumerate(headers):
                    h = str(header).lower()
                    if 'name' in h:
                        name_col = col_idx
                    if 'separat' in h and 'date' in h:
                        date_col = col_idx

                # Extract data
                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if not row or len(row) < 2 or not row[0].strip():
                        continue

                    name = row[name_col].strip() if name_col and name_col < len(row) else ''
                    sep_date = row[date_col].strip() if date_col and date_col < len(row) else ''

                    if name and sep_date:
                        if name in dates:
                            dates[name]['leaving_date'] = sep_date
                        else:
                            dates[name] = {
                                'joining_date': '',
                                'leaving_date': sep_date
                            }

    return dates

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    # Extract from payroll
    print("Extracting employee data from payroll...")
    payroll_sheets = [
        ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL', 'Nov 2024'),
        ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL', 'Dec 2024'),
        ('1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL', 'Jan 2025'),
    ]

    monthly_employees = {}
    for sheet_id, tab, month in payroll_sheets:
        rows = fetch_sheet_data(service, sheet_id, tab)
        employees = extract_employees_with_dates(rows)
        monthly_employees[month] = employees
        print(f"  {month}: {len(employees)} employees")

    # Extract dates from addition/deletion sheets
    print("\nExtracting dates from addition/deletion records...")

    # Try to get dates from the comprehensive payroll sheets
    addition_deletion_sheets = [
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'July, 2024'),
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'August 2024'),
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'September 2024'),
        ('1h-FEb5qeeqRdZsqrQGaO6H_m4l5k3NqQW6Z-_P1ES3k', 'October 2024'),
        ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL'),
        ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL'),
        ('1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL'),
        ('1T5rMIo0Apv41Tm-jDstU1qT5Lp6raFGhBNaYPIR4oe0', 'OPL'),
        ('17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc', 'OPL'),
        ('1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k', 'OPL'),
        ('1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0', 'OPL'),
        ('1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us', 'OPL'),
    ]

    all_dates = {}
    for sheet_id, tab in addition_deletion_sheets:
        rows = fetch_sheet_data(service, sheet_id, tab)
        dates = extract_addition_deletion_dates(rows)
        all_dates.update(dates)
        if dates:
            print(f"  Found {len(dates)} dates in {tab}")

    # Merge data
    print("\nMerging employee data with dates...")
    final_employees = {}

    # Start with November employees
    for name, emp_data in monthly_employees['Nov 2024'].items():
        final_employees[name] = emp_data.copy()
        if name in all_dates:
            final_employees[name]['joining_date'] = all_dates[name].get('joining_date', '')
            final_employees[name]['leaving_date'] = all_dates[name].get('leaving_date', '')

    # Get sets for comparison
    nov_set = set(monthly_employees['Nov 2024'].keys())
    dec_set = set(monthly_employees['Dec 2024'].keys())
    jan_set = set(monthly_employees['Jan 2025'].keys())

    # Leavers
    leavers = dec_set - jan_set

    print(f"\nOpening employees: {len(nov_set)}")
    print(f"Leavers: {len(leavers)}")

    # Create output
    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    # Add all employees
    for name in sorted(final_employees.keys()):
        emp = final_employees[name]
        joining = emp.get('joining_date', '')
        leaving = emp.get('leaving_date', '')

        # If they left, ensure leaving date is filled if available
        if name in leavers and not leaving and name in all_dates:
            leaving = all_dates[name].get('leaving_date', '')

        row = [
            '',
            name,
            emp.get('department', ''),
            emp.get('designation', ''),
            joining,
            leaving,
            emp.get('salary', '')
        ]
        output_rows.append(row)

    print(f"\nCreating Google Sheet with dates...")
    try:
        create_request = {
            'properties': {
                'title': 'OPL List of Joiners and Leavers 2024-2025'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G1000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print(f"\nSheet created with dates!")
        print(f"URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nTotal employees: {len(final_employees)}")
        print(f"Employees with joining dates: {sum(1 for e in final_employees.values() if e.get('joining_date'))}")
        print(f"Employees with leaving dates: {sum(1 for e in final_employees.values() if e.get('leaving_date'))}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
