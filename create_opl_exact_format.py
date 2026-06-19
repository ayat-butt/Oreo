#!/usr/bin/env python3
"""
Create OPL sheet in EXACT OWT format
"""

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

def fetch_opl_data(service, sheet_id, tab_name):
    """Fetch OPL data"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab_name}'!A1:Z500"
        ).execute()
        return result.get('values', [])
    except:
        return []

def extract_clean_employees(rows):
    """Extract employee data properly"""
    employees = {}

    if not rows or len(rows) < 2:
        return employees

    # Find header
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

    # Extract
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

    # Fetch data from all months
    sheets_data = [
        ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL', 'Nov 2024'),
        ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL', 'Dec 2024'),
        ('1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL', 'Jan 2025'),
    ]

    monthly_employees = {}

    print("Extracting OPL data...")
    for sheet_id, tab, month in sheets_data:
        rows = fetch_opl_data(service, sheet_id, tab)
        employees = extract_clean_employees(rows)
        monthly_employees[month] = employees
        print(f"  {month}: {len(employees)} employees")

    # Identify joiners and leavers
    nov_set = set(monthly_employees['Nov 2024'].keys())
    dec_set = set(monthly_employees['Dec 2024'].keys())
    jan_set = set(monthly_employees['Jan 2025'].keys())

    # All who appeared in Nov (opening balance)
    opening_employees = nov_set

    # Joiners: appeared in Dec but not Nov
    new_joiners = dec_set - nov_set

    # Leavers: appeared in Dec but not Jan
    leavers = dec_set - jan_set

    print(f"\nAnalysis:")
    print(f"  Opening (Nov 2024): {len(opening_employees)}")
    print(f"  New Joiners (Dec 2024): {len(new_joiners)}")
    print(f"  Leavers (Dec to Jan): {len(leavers)}")

    # Build output sheet rows
    output_rows = [
        [''],  # Row 0: Empty
        ['', 'List of Joiner and Leavers July 24 - June 25'],  # Row 1: Title
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],  # Row 2: Headers
    ]

    # Add opening employees (Date of Leaving filled with dates they left, or empty if stayed)
    print(f"\nAdding opening employees...")
    for name in sorted(opening_employees):
        emp = monthly_employees['Nov 2024'][name]

        # Check if they left
        if name in leavers:
            # They left - put empty in joining, leaving date to be filled
            row = [
                '',
                name,
                emp.get('department', ''),
                emp.get('designation', ''),
                '',  # Date of Joining (empty for opening)
                '',  # Date of Leaving (to be filled - they left)
                emp.get('salary', '')
            ]
        else:
            # They stayed - empty both dates or keep as is
            row = [
                '',
                name,
                emp.get('department', ''),
                emp.get('designation', ''),
                '',
                '',
                emp.get('salary', '')
            ]

        output_rows.append(row)

    # Add new joiners
    print(f"Adding new joiners...")
    for name in sorted(new_joiners):
        emp = monthly_employees['Dec 2024'][name]
        row = [
            '',
            name,
            emp.get('department', ''),
            emp.get('designation', ''),
            '',  # Date of Joining (to be filled)
            '',  # Date of Leaving (empty)
            emp.get('salary', '')
        ]
        output_rows.append(row)

    # Create the sheet
    print(f"\nCreating Google Sheet...")
    try:
        create_request = {
            'properties': {
                'title': 'OPL List of Joiners and Leavers 2024-2025'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        print(f"Created: {new_sheet_id}")

        # Write data
        update_body = {
            'values': output_rows
        }

        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G1000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print(f"\nSheet URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nData Summary:")
        print(f"  Total Opening Employees: {len(opening_employees)}")
        print(f"  New Joiners (to be dated): {len(new_joiners)}")
        print(f"  Leavers (to be dated): {len(leavers)}")
        print(f"  Total Rows: {len(output_rows) - 3}")  # -3 for header rows

        # Save ID
        with open('output/OPL_SHEET_FINAL_ID.txt', 'w') as f:
            f.write(f"OPL List of Joiners and Leavers 2024-2025\n")
            f.write(f"Sheet ID: {new_sheet_id}\n")
            f.write(f"URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}\n\n")
            f.write(f"Opening Employees: {len(opening_employees)}\n")
            f.write(f"New Joiners: {len(new_joiners)}\n")
            f.write(f"Leavers: {len(leavers)}\n")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
