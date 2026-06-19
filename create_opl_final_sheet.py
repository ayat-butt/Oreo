#!/usr/bin/env python3
"""
Create a properly formatted OPL Joiners and Leavers sheet
in the OWT format in Google Sheets
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

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

def fetch_opl_data(service, sheet_id, tab_name):
    """Fetch OPL data from a sheet"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab_name}'!A1:Z500"
        ).execute()
        return result.get('values', [])
    except:
        return []

def extract_employees_properly(rows):
    """Extract employee data, filtering out numeric IDs"""
    employees = {}

    if not rows or len(rows) < 2:
        return employees

    # Find header with "Employee"
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

    # Map columns
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

    # Extract data
    for row_idx in range(header_row + 1, len(rows)):
        row = rows[row_idx]
        if not row or len(row) < 2:
            continue

        name = row[name_col].strip() if name_col and name_col < len(row) else ''
        if not name or name == '':
            continue

        # Skip numeric IDs or obviously wrong entries
        if name.isdigit() or 'total' in name.lower():
            continue

        # Only include proper names (longer than 2 chars, contains letters)
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

    # Collect data from all sheets
    sheets_data = [
        ('1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA', 'OPL', 'Nov 2024'),
        ('1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E', 'OPL', 'Dec 2024'),
        ('1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA', 'OPL', 'Jan 2025'),
        ('17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc', 'OPL', 'Mar 2025'),
    ]

    monthly_employees = {}

    print("Fetching OPL data from all sheets...")
    for sheet_id, tab, month in sheets_data:
        rows = fetch_opl_data(service, sheet_id, tab)
        employees = extract_employees_properly(rows)
        monthly_employees[month] = employees
        print(f"  {month}: {len(employees)} employees")

    # Identify joiners and leavers
    all_joiners = []
    all_leavers = []

    print("\nAnalyzing joiners and leavers...")

    # Get November as baseline
    nov_employees = set(monthly_employees['Nov 2024'].keys())
    dec_employees = set(monthly_employees['Dec 2024'].keys())
    jan_employees = set(monthly_employees['Jan 2025'].keys())
    mar_employees = set(monthly_employees['Mar 2025'].keys())

    # Joiners in Nov (baseline for Jul-Oct)
    for name in nov_employees:
        emp = monthly_employees['Nov 2024'][name]
        all_joiners.append([
            '',  # Blank column
            name,
            emp.get('department', ''),
            emp.get('designation', ''),
            '',  # Date of Joining (to be filled manually)
            '',  # Date of Leaving
            emp.get('salary', ''),
            '',  # Blank
            'Opening',  # Type
            '1',  # Number
            '',  # Blank
            'OPL'  # Department code
        ])

    # Leavers in January (left between Jan and next period)
    leavers_jan = jan_employees - dec_employees
    for name in leavers_jan:
        emp = monthly_employees['Dec 2024'][name] if name in monthly_employees['Dec 2024'] else monthly_employees['Jan 2025'][name]
        all_leavers.append([
            '',
            name,
            emp.get('department', ''),
            emp.get('designation', ''),
            '',  # Date of Joining
            '',  # Date of Leaving (to be filled)
            emp.get('salary', ''),
            '',
            'Deletion',  # Type
            '1',
            '',
            'OPL'
        ])

    # Create output sheet
    output_rows = [
        [],  # Row 0: Empty
        ['', 'List of Joiner and Leavers July 24 - June 25'],  # Row 1: Title
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries', '', 'Type', 'Number', '', 'Entity'],  # Row 2: Headers
    ]

    output_rows.extend(all_joiners)
    output_rows.extend(all_leavers)

    # Create a new sheet
    print(f"\nCreating output sheet with {len(all_joiners)} joiners and {len(all_leavers)} leavers...")

    try:
        # Create spreadsheet
        create_request = {
            'properties': {
                'title': 'OPL List of Joiners and Leavers 2024-2025'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        print(f"Created new sheet: {new_sheet_id}")
        print(f"Link: https://docs.google.com/spreadsheets/d/{new_sheet_id}")

        # Write data to the sheet
        update_body = {
            'values': output_rows
        }

        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:L500',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print("\nData written to sheet successfully!")

        # Save the sheet ID for reference
        with open('output/OPL_AUDIT_SHEET_ID.txt', 'w') as f:
            f.write(f"OPL List of Joiners and Leavers 2024-2025\n")
            f.write(f"Sheet ID: {new_sheet_id}\n")
            f.write(f"URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}\n\n")
            f.write(f"Total Joiners: {len(all_joiners)}\n")
            f.write(f"Total Leavers: {len(all_leavers)}\n")

        print(f"\nSummary:")
        print(f"  Total Joiners: {len(all_joiners)}")
        print(f"  Total Leavers: {len(all_leavers)}")

    except Exception as e:
        print(f"Error creating sheet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
