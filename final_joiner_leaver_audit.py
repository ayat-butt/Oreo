#!/usr/bin/env python3
"""
FINAL: Comprehensive OPL Joiner & Leaver Audit - July 2024 to June 2025
Uses verified sheet IDs and accurate employee counts
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import pandas as pd
import io

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

def extract_employees_from_excel(drive_service, file_id, month_name):
    """Extract employee names from Excel file (July-October)"""
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()
        xls = pd.ExcelFile(io.BytesIO(file_content))

        employees = {}

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)

            # Find employee name column
            employee_col = None
            dept_col = None

            for col in df.columns:
                col_lower = str(col).lower()
                if ('employee' in col_lower and 'name' in col_lower) or col_lower == 'name':
                    employee_col = col
                elif 'depart' in col_lower:
                    dept_col = col

            if employee_col is None:
                continue

            # Extract employees
            for idx, row in df.iterrows():
                name = str(row[employee_col]).strip() if pd.notna(row[employee_col]) else ''

                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                dept = str(row[dept_col]).strip() if dept_col and pd.notna(row[dept_col]) else ''
                if name not in employees:
                    employees[name] = {'department': dept}

        return employees

    except Exception as e:
        print(f"  Error reading {month_name}: {str(e)[:100]}")
        return {}

def extract_employees_from_sheet(sheets_service, sheet_id, month_name):
    """Extract employee names from Google Sheet (August onwards)"""
    employees = {}

    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        # For early sheets (Aug-Oct), read first available sheet; for later sheets, read OPL sheet
        sheet_to_read = None

        # Try to find OPL sheet first (Nov-June)
        for sheet in sheets:
            if sheet['properties']['title'].upper() == 'OPL':
                sheet_to_read = sheet
                break

        # If no OPL sheet, use first sheet (Aug-Oct)
        if sheet_to_read is None and sheets:
            sheet_to_read = sheets[0]

        if sheet_to_read is None:
            return employees

        sheet_name = sheet_to_read['properties']['title']
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A1:Z1000"
        ).execute()

        rows = result.get('values', [])
        if not rows:
            return employees

        # Find header row (first row with employee/name info)
        header_row = 0  # Default to first row

        headers = rows[header_row]
        name_col = None
        dept_col = None

        # Find columns (handle various naming conventions)
        for col_idx, header in enumerate(headers):
            h = str(header).lower().strip()
            # Match various employee name column names
            if name_col is None and (h == 'employee' or h == 'name' or h == 'employee name' or ('employee' in h and 'name' in h)):
                name_col = col_idx
            elif 'depart' in h:
                dept_col = col_idx

        if name_col is None:
            return employees

        # Extract employees
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if not row or len(row) <= name_col:
                continue

            name = str(row[name_col]).strip() if name_col < len(row) else ''
            if not name or 'total' in name.lower() or len(name) < 3:
                continue

            dept = str(row[dept_col]).strip() if dept_col and dept_col < len(row) else ''
            if name not in employees:
                employees[name] = {'department': dept}

        return employees

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        return {}

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("FINAL COMPREHENSIVE OPL AUDIT: JULY 2024 - JUNE 2025")
    print("="*120)
    print("\nMethod: Month-by-Month Cross-Checking")
    print("- Leavers: Present in Month X but NOT in Month X+1")
    print("- Joiners: Present in Month X+1 but NOT in Month X")
    print("- Excluded: Present in both months\n")

    all_sheets = {
        'July 2024': ('1NLyPSfEO7N92EjGIBy6EnrrjvWmE7QTi', 'excel'),
        'August 2024': ('1jBlbB-Ff54udES4o_G_-qhB8aAuW53Hb1jRlGNDmZ3E', 'sheets'),
        'September 2024': ('1IklN-MJqHjKlXI6s1B3I58_JGnOi0I0tEoO0rf3wkwY', 'sheets'),
        'October 2024': ('1Fi_BVfQAwDi5tSPhvRWK6dPSgCOPVYoBOhNQ81zcTBI', 'sheets'),
        'November 2024': ('1wdTogupsdtkcOEXgQWNwsiJNnUOwx-87JYcpv6MSop4', 'sheets'),
        'December 2024': ('1_A5o1Aln9AjEmjX-BzXyWfHdzLajYvwiRVmRtiKH4hs', 'sheets'),
        'January 2025': ('14rfFm49DNyESepj5Lfux1OG1QYbv5QtDTUXYh1FuNUU', 'sheets'),
        'February 2025': ('1e83npqk4HQmm0_ELlbdqJFZDXwbkz94V4RGUjpdOzE0', 'sheets'),
        'March 2025': ('1ahND0ab4mIOe1_dduUt-2tuxKvdugoEyNd2qh8HV5TQ', 'sheets'),
        'April 2025': ('1cENuT5O49O5f-ut621XlJqQ0yWFni0x6G8TNAzK6hzU', 'sheets'),
        'May 2025': ('1drSWY44h-INF3aE6TIvrqT-MFuXc1DTLoWrFMBXxUNU', 'sheets'),
        'June 2025': ('1C6sZRGVqvLrt5kKMx7jwIw7EoI4tbgHeqpmohScPXIo', 'sheets'),
    }

    monthly_data = {}

    # Read all months
    print("Reading employee data from all months:")
    for month, (sheet_id, source_type) in all_sheets.items():
        print(f"  {month}...", end=" ", flush=True)

        if source_type == 'excel':
            employees = extract_employees_from_excel(drive_service, sheet_id, month)
        else:
            employees = extract_employees_from_sheet(sheets_service, sheet_id, month)

        monthly_data[month] = employees
        print(f"{len(employees)} employees")

    # CROSS-CHECKING LOGIC
    print("\n" + "="*120)
    print("MONTH-BY-MONTH CROSS-CHECKING")
    print("="*120)

    joiner_leaver_records = {}
    months_ordered = list(monthly_data.keys())

    for i in range(len(months_ordered) - 1):
        current_month = months_ordered[i]
        next_month = months_ordered[i + 1]

        current_employees = set(monthly_data[current_month].keys())
        next_employees = set(monthly_data[next_month].keys())

        # LEAVERS
        leavers = current_employees - next_employees
        print(f"\n{current_month} -> {next_month}:")
        print(f"  Leavers: {len(leavers)}")

        for name in sorted(leavers):
            if name not in joiner_leaver_records:
                joiner_leaver_records[name] = {
                    'joining_month': 'July 2024',
                    'leaving_month': next_month,
                    'department': monthly_data[current_month][name].get('department', ''),
                }
            else:
                joiner_leaver_records[name]['leaving_month'] = next_month

        # JOINERS
        joiners = next_employees - current_employees
        print(f"  Joiners: {len(joiners)}")

        for name in sorted(joiners):
            if name not in joiner_leaver_records:
                joiner_leaver_records[name] = {
                    'joining_month': next_month,
                    'leaving_month': None,
                    'department': monthly_data[next_month][name].get('department', ''),
                }

        # CONTINUOUSLY EMPLOYED
        continuous = current_employees & next_employees
        print(f"  Continuously employed: {len(continuous)} (EXCLUDED)")

    print(f"\n" + "="*120)
    print(f"TOTAL UNIQUE JOINERS & LEAVERS: {len(joiner_leaver_records)}")
    print("="*120)

    # CREATE OUTPUT SHEET
    print(f"\nCreating final output sheet with {len(joiner_leaver_records)} records...\n")

    output_rows = []
    output_rows.append([''])
    output_rows.append(['', 'List of Joiner and Leavers July 24 - June 25'])
    output_rows.append(['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries'])

    date_map = {
        'July 2024': ('01-07-2024', '31-07-2024'),
        'August 2024': ('01-08-2024', '31-08-2024'),
        'September 2024': ('01-09-2024', '30-09-2024'),
        'October 2024': ('01-10-2024', '31-10-2024'),
        'November 2024': ('01-11-2024', '30-11-2024'),
        'December 2024': ('01-12-2024', '31-12-2024'),
        'January 2025': ('01-01-2025', '31-01-2025'),
        'February 2025': ('01-02-2025', '28-02-2025'),
        'March 2025': ('01-03-2025', '31-03-2025'),
        'April 2025': ('01-04-2025', '30-04-2025'),
        'May 2025': ('01-05-2025', '31-05-2025'),
        'June 2025': ('01-06-2025', '30-06-2025'),
    }

    for name in sorted(joiner_leaver_records.keys()):
        record = joiner_leaver_records[name]

        joining_date = ''
        if record['joining_month'] in date_map:
            joining_date = date_map[record['joining_month']][0]

        leaving_date = ''
        if record['leaving_month'] and record['leaving_month'] in date_map:
            leaving_date = date_map[record['leaving_month']][1]

        output_rows.append([
            '',
            name,
            record['department'],
            '',
            joining_date,
            leaving_date,
            ''
        ])

    # Create Google Sheet
    try:
        create_request = {
            'properties': {
                'title': 'OPL Joiners & Leavers Jul24-Jun25 (FINAL ACCURATE)'
            }
        }

        spreadsheet = sheets_service.spreadsheets().create(body=create_request).execute()
        new_sheet_id = spreadsheet['spreadsheetId']

        update_body = {'values': output_rows}
        sheets_service.spreadsheets().values().update(
            spreadsheetId=new_sheet_id,
            range='Sheet1!A1:G10000',
            valueInputOption='RAW',
            body=update_body
        ).execute()

        print("="*120)
        print("FINAL ACCURATE AUDIT SHEET CREATED")
        print("="*120)
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nAudit Summary:")
        print(f"  Total Joiners & Leavers: {len(joiner_leaver_records)}")
        print(f"  Period: July 2024 - June 2025")
        print(f"  Method: Cross-checked month-by-month")
        print(f"  Format: OWT standard")
        print(f"\nReady for audit submission!")

    except Exception as e:
        print(f"Error creating sheet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
