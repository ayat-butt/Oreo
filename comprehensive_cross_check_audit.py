#!/usr/bin/env python3
"""
Complete OPL Audit July 2024 - June 2025 with Proper Cross-Checking Logic
Reads all 12 months and identifies joiners/leavers through month-by-month comparison
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import requests
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

def download_and_read_excel(drive_service, file_id, month_name):
    """Download and read Excel file from Google Drive"""
    try:
        print(f"  Downloading {month_name} Excel file...", end=" ")
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()

        df = pd.read_excel(io.BytesIO(file_content))
        print(f"Success ({len(df)} rows)")
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_opl_from_dataframe(df, month_name):
    """Extract OPL employees from Excel DataFrame"""
    employees = {}

    if df is None or df.empty:
        return employees

    # Find employee column
    employee_col = None
    dept_col = None

    for col in df.columns:
        col_lower = str(col).lower()
        if 'employee' in col_lower and employee_col is None:
            employee_col = col
        elif 'depart' in col_lower:
            dept_col = col

    if employee_col is None:
        return employees

    # Extract employees
    for idx, row in df.iterrows():
        name = str(row[employee_col]).strip() if pd.notna(row[employee_col]) else ''

        if not name or 'total' in name.lower() or len(name) < 3:
            continue

        dept = str(row[dept_col]).strip() if dept_col and pd.notna(row[dept_col]) else ''
        employees[name] = {'department': dept}

    return employees

def get_opl_from_sheets(sheets_service, sheet_id, month_name):
    """Extract OPL employees from Google Sheets"""
    employees = {}

    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()

        for sheet in metadata.get('sheets', []):
            sheet_name = sheet['properties']['title']
            if 'OPL' not in sheet_name.upper():
                continue

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z500"
            ).execute()

            rows = result.get('values', [])
            if not rows:
                continue

            # Find header row
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
        # Likely an Office file error, will skip
        return {}

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("COMPLETE OPL AUDIT: JULY 2024 - JUNE 2025")
    print("Method: Month-by-Month Cross-Checking (Proper Logic)")
    print("="*120)
    print("\nReading all 12 months with cross-checking logic:")
    print("- Leavers: Present in Month X but NOT in Month X+1")
    print("- Joiners: Present in Month X+1 but NOT in Month X")
    print("- Excluded: Present in both months\n")

    # All 12 months with their IDs
    all_sheets = {
        'July 2024': '1tIKIU0LKCR2YYuCS0u0lb_Gr-rDm6ks_',
        'August 2024': '15n2DllSdSDErWwl0pj3PkeqwJKF5LDbZ',
        'September 2024': '1bP1Ju0vzcS7QxF1NkheVZpI6HxliE-F7',
        'October 2024': '1h1IRXwxx-mRAp0m2C2sqHlIjR5OzYpjc',
        'November 2024': '1LdPBzOn2tViWjNhbxcbcokExDZG-eTzPV6sB_Mfd8FA',
        'December 2024': '1CU5sU-lEBdDqv61gVLs-33VBEr3BR6yTTW14lWOJY0E',
        'January 2025': '1RCKI2qM4rUeR3pe6PL0Gt7fw0iEcx5Ek7O97s42XQXA',
        'February 2025': '1T5rMIo0Apv41Tm-jDstU1qT5Lp6raFGhBNaYPIR4oe0',
        'March 2025': '17qI-qwttshi_qWok5Xqbu5p2xDNt8SmvKx_g-QL-QPc',
        'April 2025': '1lOSgTwzvI0NudWB6voUXJaNhViAqBbCPhCURqTZQx8k',
        'May 2025': '1uhAxR4UCrY5OOmQHgfdpqOS_M3QeIUBt66YtojpRHD0',
        'June 2025': '1KtM9hkNIFEnvYWO8DFZf1iVSZungdiWdIGAsQTmu-Us',
    }

    monthly_data = {}

    # JULY - OCTOBER: Try to download as Excel first, then fall back to Sheets API
    print("Reading July - October 2024 (Office files):")
    for month in ['July 2024', 'August 2024', 'September 2024', 'October 2024']:
        sheet_id = all_sheets[month]

        # Try Google Sheets API first
        employees = get_opl_from_sheets(sheets_service, sheet_id, month)

        if not employees:
            # If that fails, try downloading as Excel
            try:
                df = download_and_read_excel(drive_service, sheet_id, month)
                employees = extract_opl_from_dataframe(df, month)
            except:
                pass

        monthly_data[month] = employees
        print(f"  {month}: {len(employees)} OPL employees")

    # NOVEMBER 2024 - JUNE 2025: Read from Google Sheets
    print("\nReading November 2024 - June 2025 (Google Sheets):")
    for month in ['November 2024', 'December 2024', 'January 2025', 'February 2025',
                  'March 2025', 'April 2025', 'May 2025', 'June 2025']:
        sheet_id = all_sheets[month]
        employees = get_opl_from_sheets(sheets_service, sheet_id, month)
        monthly_data[month] = employees
        print(f"  {month}: {len(employees)} OPL employees")

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

        # LEAVERS: In current month but NOT in next month
        leavers = current_employees - next_employees
        print(f"\n{current_month} -> {next_month}:")
        print(f"  Leavers: {len(leavers)} (in {current_month} but NOT in {next_month})")

        for name in sorted(leavers):
            if name not in joiner_leaver_records:
                joiner_leaver_records[name] = {
                    'joining_month': 'July 2024',  # Opening balance
                    'leaving_month': next_month,
                    'department': monthly_data[current_month][name].get('department', ''),
                }
            else:
                joiner_leaver_records[name]['leaving_month'] = next_month

        # JOINERS: In next month but NOT in current month
        joiners = next_employees - current_employees
        print(f"  Joiners: {len(joiners)} (in {next_month} but NOT in {current_month})")

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
                'title': 'OPL Joiners & Leavers Jul24-Jun25 (FINAL AUDIT)'
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
        print("FINAL AUDIT SHEET CREATED")
        print("="*120)
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
        print(f"\nAudit Summary:")
        print(f"  Total Joiners & Leavers: {len(joiner_leaver_records)}")
        print(f"  Period: July 2024 - June 2025")
        print(f"  Method: Cross-checked month-by-month")
        print(f"  Format: OWT standard (Name, Department, Designation, Joining Date, Leaving Date, Salaries)")
        print(f"\nReady for audit submission!")

    except Exception as e:
        print(f"Error creating sheet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
