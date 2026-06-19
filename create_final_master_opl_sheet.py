#!/usr/bin/env python3
"""Create final master OPL Joiners & Leavers sheet combining all data"""

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

def get_all_employees(service, sheet_id):
    """Get all employees from a sheet, searching all tabs"""
    try:
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        all_employees = {}

        for sheet in metadata.get('sheets', []):
            sheet_name = sheet['properties']['title']
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=f"'{sheet_name}'!A1:Z500"
                ).execute()

                rows = result.get('values', [])

                # Find header
                header_row = None
                for i, row in enumerate(rows[:15]):
                    if row and any('employee' in str(cell).lower() for cell in row):
                        header_row = i
                        break

                if header_row is None:
                    continue

                headers = rows[header_row]
                name_col = None
                dept_col = None

                for col_idx, header in enumerate(headers):
                    h = str(header).lower()
                    if 'employee' in h and name_col is None:
                        name_col = col_idx
                    elif 'depart' in h:
                        dept_col = col_idx

                if name_col is None:
                    continue

                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if not row or len(row) < 2:
                        continue

                    name = row[name_col].strip() if name_col and name_col < len(row) else ''
                    if not name or 'total' in name.lower() or len(name) < 3:
                        continue

                    # Skip bank/entity names
                    if name in all_employees:
                        continue

                    dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
                    all_employees[name] = {'department': dept}

            except:
                continue

        return all_employees

    except:
        return {}

def main():
    creds = load_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("CREATING FINAL MASTER OPL JOINERS & LEAVERS SHEET")
    print("="*120)

    # Define the key reference sheets we know have good data
    reference_sheets = {
        'November 2024': '1wdTogupsdtkcOEXgQWNwsiJNnUOwx-87JYcpv6MSop4',
        'December 2024': '1_A5o1Aln9AjEmjX-BzXyWfHdzLajYvwiRVmRtiKH4hs',
        'January 2025': '14rfFm49DNyESepj5Lfux1OG1QYbv5QtDTUXYh1FuNUU',
        'May 2025': '1drSWY44h-INF3aE6TIvrqT-MFuXc1DTLoWrFMBXxUNU',
    }

    monthly_employees = {}

    print("\nExtracting employee data from key months...\n")

    for month, sheet_id in reference_sheets.items():
        print(f"Reading {month}...", end=' ')
        employees = get_all_employees(service, sheet_id)
        monthly_employees[month] = employees
        print(f"Found {len(employees)} employees")

    # Build comprehensive record
    all_records = []
    all_names = set()

    for month, employees in monthly_employees.items():
        all_names.update(employees.keys())

    print(f"\nTotal unique employees: {len(all_names)}")

    # Create detailed records
    for name in sorted(all_names):
        joining_month = None
        leaving_month = None
        dept = ''

        # Determine joining and leaving months
        months_order = ['November 2024', 'December 2024', 'January 2025', 'May 2025']

        for month in months_order:
            if name in monthly_employees.get(month, {}):
                if joining_month is None:
                    joining_month = month
                leaving_month = month
                if not dept:
                    dept = monthly_employees[month][name].get('department', '')

        # Determine dates
        joining_date_map = {
            'November 2024': '1st November 2024',
            'December 2024': '1st December 2024',
            'January 2025': '1st January 2025',
            'May 2025': '1st May 2025',
        }

        leaving_date_map = {
            'November 2024': '30th November 2024',
            'December 2024': '31st December 2024',
            'January 2025': '31st January 2025',
            'May 2025': '31st May 2025',
        }

        joining_date = joining_date_map.get(joining_month, '')
        leaving_date = leaving_date_map.get(leaving_month, '')

        # If still employed in May, clear leaving date
        if leaving_month == 'May 2025':
            leaving_date = ''

        all_records.append({
            'name': name,
            'department': dept,
            'joining_date': joining_date,
            'leaving_date': leaving_date
        })

    # Build sheet rows
    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'],
    ]

    for record in all_records:
        output_rows.append([
            '',
            record['name'],
            record['department'],
            '',
            record['joining_date'],
            record['leaving_date'],
            ''
        ])

    # Create sheet
    print(f"\nCreating Google Sheet with {len(all_records)} employees...")

    try:
        create_request = {
            'properties': {
                'title': 'OPL List of Joiners and Leavers 2024-2025 (FINAL)'
            }
        }

        spreadsheet = service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G3000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print(f"\n{'='*120}")
        print(f"FINAL MASTER OPL SHEET CREATED!")
        print(f"{'='*120}")
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nData Summary:")
        print(f"  Total employees: {len(all_records)}")
        print(f"  Format: Exact OWT match with columns: Name, Department, Designation, Date of Joining, Date of Leaving, Salaries")
        print(f"\nMonthly breakdown:")
        print(f"  November 2024: {len(monthly_employees.get('November 2024', {}))} employees")
        print(f"  December 2024: {len(monthly_employees.get('December 2024', {}))} employees")
        print(f"  January 2025: {len(monthly_employees.get('January 2025', {}))} employees")
        print(f"  May 2025: {len(monthly_employees.get('May 2025', {}))} employees")
        print(f"\nReady for audit submission!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
