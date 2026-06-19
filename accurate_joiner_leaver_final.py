#!/usr/bin/env python3
"""
FINAL: OPL Joiner & Leaver Audit July 2024 - June 2025
Using verified employee counts and proper data extraction
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

def extract_from_excel(drive_service, file_id):
    """Extract employee names from Excel (July-Oct)"""
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()
        xls = pd.ExcelFile(io.BytesIO(file_content))

        employees = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)

            name_col = None
            dept_col = None

            for col in df.columns:
                col_lower = str(col).lower()
                if ('employee' in col_lower and 'name' in col_lower) or col_lower == 'name':
                    name_col = col
                elif 'depart' in col_lower:
                    dept_col = col

            if name_col is None:
                continue

            for idx, row in df.iterrows():
                name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ''
                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                dept = str(row[dept_col]).strip() if dept_col and pd.notna(row[dept_col]) else ''
                if name not in employees:
                    employees[name] = {'department': dept}

        return employees
    except:
        return {}

def extract_from_sheets(sheets_service, sheet_id):
    """Extract employee names from Google Sheets (Aug onwards)"""
    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        # Find OPL sheet, else use first sheet
        target_sheet = None
        for sheet in sheets:
            if 'OPL' in sheet['properties']['title']:
                target_sheet = sheet
                break
        if not target_sheet and sheets:
            target_sheet = sheets[0]

        if not target_sheet:
            return {}

        sheet_name = target_sheet['properties']['title']
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A1:Z1000"
        ).execute()

        rows = result.get('values', [])
        if not rows:
            return {}

        headers = rows[0]
        name_col = None
        dept_col = None

        for col_idx, header in enumerate(headers):
            h = str(header).lower().strip()
            if name_col is None and ('employee' in h or h == 'name'):
                name_col = col_idx
            elif 'depart' in h:
                dept_col = col_idx

        if name_col is None:
            return {}

        employees = {}
        for row_idx in range(1, len(rows)):
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
    except:
        return {}

def main():
    creds = load_credentials()
    if not creds:
        return

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("FINAL OPL JOINER & LEAVER AUDIT: JULY 2024 - JUNE 2025")
    print("="*120)
    print()

    sheets_config = {
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

    print("Reading employee data from all months:")
    for month, (sheet_id, source_type) in sheets_config.items():
        print(f"  {month}...", end=" ", flush=True)

        if source_type == 'excel':
            employees = extract_from_excel(drive_service, sheet_id)
        else:
            employees = extract_from_sheets(sheets_service, sheet_id)

        monthly_data[month] = employees
        print(f"{len(employees)} employees")

    print("\n" + "="*120)
    print("MONTH-BY-MONTH CROSS-CHECKING")
    print("="*120)

    joiner_leaver_records = {}
    months_list = list(monthly_data.keys())

    for i in range(len(months_list) - 1):
        current_month = months_list[i]
        next_month = months_list[i + 1]

        current_set = set(monthly_data[current_month].keys())
        next_set = set(monthly_data[next_month].keys())

        leavers = current_set - next_set
        joiners = next_set - current_set

        print(f"\n{current_month} ({len(current_set)}) -> {next_month} ({len(next_set)}):")
        print(f"  Leavers: {len(leavers)} | Joiners: {len(joiners)} | Continuous: {len(current_set & next_set)}")

        for name in sorted(leavers):
            if name not in joiner_leaver_records:
                joiner_leaver_records[name] = {
                    'joining_month': 'July 2024',
                    'leaving_month': next_month,
                    'department': monthly_data[current_month][name].get('department', ''),
                }
            else:
                joiner_leaver_records[name]['leaving_month'] = next_month

        for name in sorted(joiners):
            if name not in joiner_leaver_records:
                joiner_leaver_records[name] = {
                    'joining_month': next_month,
                    'leaving_month': None,
                    'department': monthly_data[next_month][name].get('department', ''),
                }

    print("\n" + "="*120)
    print(f"TOTAL UNIQUE JOINERS & LEAVERS: {len(joiner_leaver_records)}")
    print("="*120)

    # Create output
    print(f"\nCreating Google Sheet with {len(joiner_leaver_records)} records...")

    output_rows = [
        [''],
        ['', 'List of Joiner and Leavers July 24 - June 25'],
        ['', 'Name', 'Department', 'Designation', 'Date of Joining', 'Date of Leaving', 'Salaries']
    ]

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

        joining_date = date_map.get(record['joining_month'], ('', ''))[0]
        leaving_date = ''
        if record['leaving_month']:
            leaving_date = date_map.get(record['leaving_month'], ('', ''))[1]

        output_rows.append([
            '', name, record['department'], '', joining_date, leaving_date, ''
        ])

    # Upload to Google Sheets
    try:
        spreadsheet = sheets_service.spreadsheets().create(
            body={'properties': {'title': 'OPL Joiners & Leavers Jul24-Jun25 (FINAL)'}}
        ).execute()

        sheet_id = spreadsheet['spreadsheetId']
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='Sheet1!A1:G10000',
            valueInputOption='RAW',
            body={'values': output_rows}
        ).execute()

        print("\n" + "="*120)
        print("AUDIT SHEET CREATED SUCCESSFULLY")
        print("="*120)
        print(f"\nURL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        print(f"Total Joiners & Leavers: {len(joiner_leaver_records)}")
        print(f"Format: OWT standard")
        print(f"\nReady for audit submission!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
