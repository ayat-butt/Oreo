#!/usr/bin/env python3
"""
Verify OPL employee counts for July 2024 - June 2025
- July-October: Count by "Employee Grade" = "Orenda Private Limited"
- November-June: Count all employees (already OPL-only sheets)
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

def count_opl_in_excel(drive_service, sheet_id, month_name):
    """Count OPL employees in Excel file (July-October)"""
    try:
        request = drive_service.files().get_media(fileId=sheet_id)
        file_content = request.execute()
        xls = pd.ExcelFile(io.BytesIO(file_content))

        opl_count = 0
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)

            # Find entity column
            entity_col = None
            employee_col = None

            for col in df.columns:
                col_lower = str(col).lower()
                if 'employee' in col_lower and 'name' in col_lower and employee_col is None:
                    employee_col = col
                elif 'grade' in col_lower or 'entity' in col_lower or 'company' in col_lower:
                    entity_col = col

            if employee_col is None or entity_col is None:
                continue

            # Count OPL employees
            for idx, row in df.iterrows():
                name = str(row[employee_col]).strip() if pd.notna(row[employee_col]) else ''

                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                if pd.notna(row[entity_col]):
                    if 'Orenda Private Limited' in str(row[entity_col]):
                        opl_count += 1

        return opl_count

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        return 0

def count_opl_in_google_sheet(sheets_service, sheet_id, month_name, is_opl_only=False):
    """Count OPL employees in Google Sheet"""
    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        opl_employees = {}  # Use dict to avoid counting duplicates

        for sheet in sheets:
            sheet_name = sheet['properties']['title']

            # For OPL-only sheets (Nov-June): Only process sheets with "OPL" in name
            if is_opl_only and 'OPL' not in sheet_name.upper():
                continue

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"'{sheet_name}'!A1:Z500"
            ).execute()

            rows = result.get('values', [])
            if not rows:
                continue

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
            entity_col = None

            # Find name column
            for col_idx, header in enumerate(headers):
                h = str(header).lower()
                if ('employee' in h or 'name' in h) and name_col is None:
                    name_col = col_idx
                elif not is_opl_only and any(x in h for x in ['grade', 'entity', 'company', 'division']):
                    entity_col = col_idx

            if name_col is None:
                continue

            # For Nov-June: Just count all employees in OPL sheets
            if is_opl_only:
                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if not row or len(row) <= name_col:
                        continue

                    name = str(row[name_col]).strip() if name_col < len(row) else ''
                    if not name or 'total' in name.lower() or len(name) < 3:
                        continue

                    opl_employees[name] = True
            else:
                # For mixed sheets: Filter by entity column
                if entity_col is None:
                    continue

                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if not row or len(row) <= name_col:
                        continue

                    name = str(row[name_col]).strip() if name_col < len(row) else ''
                    if not name or 'total' in name.lower() or len(name) < 3:
                        continue

                    if entity_col < len(row) and 'Orenda Private Limited' in str(row[entity_col]):
                        opl_employees[name] = True

        return len(opl_employees)

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        return 0

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    print("="*120)
    print("OPL EMPLOYEE COUNT VERIFICATION: JULY 2024 - JUNE 2025")
    print("="*120)
    print()

    sheets_data = {
        'July 2024': ('1NLyPSfEO7N92EjGIBy6EnrrjvWmE7QTi', 'excel', False),
        'August 2024': ('1jBlbB-Ff54udES4o_G_-qhB8aAuW53Hb1jRlGNDmZ3E', 'sheets', False),
        'September 2024': ('1IklN-MJqHjKlXI6s1B3I58_JGnOi0I0tEoO0rf3wkwY', 'sheets', False),
        'October 2024': ('1Fi_BVfQAwDi5tSPhvRWK6dPSgCOPVYoBOhNQ81zcTBI', 'sheets', False),
        'November 2024': ('1wdTogupsdtkcOEXgQWNwsiJNnUOwx-87JYcpv6MSop4', 'sheets', True),
        'December 2024': ('1_A5o1Aln9AjEmjX-BzXyWfHdzLajYvwiRVmRtiKH4hs', 'sheets', True),
        'January 2025': ('14rfFm49DNyESepj5Lfux1OG1QYbv5QtDTUXYh1FuNUU', 'sheets', True),
        'February 2025': ('1e83npqk4HQmm0_ELlbdqJFZDXwbkz94V4RGUjpdOzE0', 'sheets', True),
        'March 2025': ('1ahND0ab4mIOe1_dduUt-2tuxKvdugoEyNd2qh8HV5TQ', 'sheets', True),
        'April 2025': ('1cENuT5O49O5f-ut621XlJqQ0yWFni0x6G8TNAzK6hzU', 'sheets', True),
        'May 2025': ('1drSWY44h-INF3aE6TIvrqT-MFuXc1DTLoWrFMBXxUNU', 'sheets', True),
        'June 2025': ('1C6sZRGVqvLrt5kKMx7jwIw7EoI4tbgHeqpmohScPXIo', 'sheets', True),
    }

    monthly_counts = {}

    for month, (sheet_id, source_type, is_opl_only) in sheets_data.items():
        print(f"Reading {month:<20}", end=" ", flush=True)

        if source_type == 'excel':
            count = count_opl_in_excel(drive_service, sheet_id, month)
        else:
            count = count_opl_in_google_sheet(sheets_service, sheet_id, month, is_opl_only)

        monthly_counts[month] = count
        print(f"... {count:>3} OPL employees")

    print()
    print("="*120)
    print("SUMMARY: OPL EMPLOYEE COUNTS BY MONTH")
    print("="*120)
    print()

    total = 0
    for month in sheets_data.keys():
        count = monthly_counts[month]
        total += count
        print(f"  {month:<20} : {count:>3} employees")

    print()
    print(f"  {'TOTAL':<20} : {total:>3} employees")
    print()

if __name__ == '__main__':
    main()
