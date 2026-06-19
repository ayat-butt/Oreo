#!/usr/bin/env python3
"""
Create OPL sheet with estimated dates based on payroll data
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            import json
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

def fetch_opl_data(service, sheet_id, tab_name):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab_name}'!A1:Z500"
        ).execute()
        return result.get('values', [])
    except:
        return []

def extract_employees(rows):
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
            'designation': designation
        }

    return employees

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    # Fetch data
    print("Extracting OPL employee data...")
    payroll_sheets = [
        ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL', 'Nov 2024'),
        ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL', 'Dec 2024'),
        ('1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL', 'Jan 2025'),
    ]

    monthly_employees = {}
    for sheet_id, tab, month in payroll_sheets:
        rows = fetch_opl_data(service, sheet_id, tab)
        employees = extract_employees(rows)
        monthly_employees[month] = employees
        print(f"  {month}: {len(employees)} employees")

    # Analyze
    nov_set = set(monthly_employees['Nov 2024'].keys())
    dec_set = set(monthly_employees['Dec 2024'].keys())
    jan_set = set(monthly_employees['Jan 2025'].keys())

    opening = nov_set
    leavers = dec_set - jan_set

    print(f"\nAnalysis:")
    print(f"  Opening: {len(opening)}")
    print(f"  Leavers (Dec-Jan): {len(leavers)}")

    # Build output with estimated dates
    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    # Process all employees
    all_names = sorted(opening)

    for name in all_names:
        emp = monthly_employees['Nov 2024'][name]

        # Determine dates
        if name in leavers:
            # They left - use December as leaving month
            joining_date = ''  # Not a new joiner
            leaving_date = '31st December 2024'  # Estimated from payroll
        else:
            # Still employed
            joining_date = ''  # Opening employee
            leaving_date = ''  # Still employed

        row = [
            '',
            name,
            emp.get('department', ''),
            emp.get('designation', ''),
            joining_date,
            leaving_date,
            emp.get('salary', '')
        ]
        output_rows.append(row)

    # Create sheet
    print(f"\nCreating Google Sheet with {len(all_names)} employees...")
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

        print(f"\nSheet created successfully!")
        print(f"URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nContents:")
        print(f"  Total Opening Employees: {len(opening)}")
        print(f"  Employees with Leave Dates: {len(leavers)}")
        print(f"\nNote: Dates are estimated from payroll data.")
        print(f"Please verify and update with actual HR records.")

        # Save reference
        with open('output/OPL_SHEET_WITH_DATES_ID.txt', 'w') as f:
            f.write(f"OPL List of Joiners and Leavers 2024-2025\n")
            f.write(f"Sheet ID: {new_sheet_id}\n")
            f.write(f"URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}\n\n")
            f.write(f"CONTENTS:\n")
            f.write(f"Total Opening Employees: {len(opening)}\n")
            f.write(f"Employees who left: {len(leavers)}\n\n")
            f.write(f"NOTE:\n")
            f.write(f"- Opening employees (Nov 2024 payroll): Please fill in actual joining dates\n")
            f.write(f"- Leavers: Dates estimated as '31st December 2024' based on payroll disappearance\n")
            f.write(f"- Please verify all dates against HR records before audit submission\n")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
