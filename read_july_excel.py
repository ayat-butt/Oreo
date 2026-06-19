#!/usr/bin/env python3
"""Read July 2024 Excel file and count OPL employees"""

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

def main():
    creds = load_credentials()
    if not creds:
        return

    drive_service = build('drive', 'v3', credentials=creds)

    # July 2024 file ID
    file_id = '1NLyPSfEO7N92EjGIBy6EnrrjvWmE7QTi'

    print("="*120)
    print("READING JULY 2024 EXCEL FILE")
    print("="*120)
    print(f"\nFile ID: {file_id}")

    try:
        # Download file
        print("\nDownloading Excel file...")
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()

        print("File downloaded successfully")
        print("\nReading Excel sheets...\n")

        # Read all sheets
        xls = pd.ExcelFile(io.BytesIO(file_content))

        print(f"Total sheets in workbook: {len(xls.sheet_names)}")
        print(f"Sheet names: {xls.sheet_names}\n")

        # Check each sheet for OPL data
        opl_count = 0
        for sheet_name in xls.sheet_names:
            print(f"\nSheet: '{sheet_name}'")
            print("-" * 80)

            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)

            print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
            print(f"  Columns: {list(df.columns)[:8]}")

            # Look for employee column
            employee_col = None
            dept_col = None

            for col in df.columns:
                col_lower = str(col).lower()
                if 'employee' in col_lower and employee_col is None:
                    employee_col = col
                elif 'depart' in col_lower:
                    dept_col = col

            if employee_col is None:
                print(f"  No employee column found")
                continue

            # Count valid employees
            employees = []
            for idx, row in df.iterrows():
                name = str(row[employee_col]).strip() if pd.notna(row[employee_col]) else ''

                if not name or 'total' in name.lower() or len(name) < 3:
                    continue

                dept = str(row[dept_col]).strip() if dept_col and pd.notna(row[dept_col]) else ''
                employees.append({'name': name, 'department': dept})

            if employees:
                print(f"  Employees found: {len(employees)}")
                if 'OPL' in sheet_name.upper() or 'ORENDA' in sheet_name.upper():
                    opl_count = len(employees)
                    print(f"  [OPL DATA FOUND] {opl_count} employees")
                    print(f"\n  First 15 employees:")
                    for i, emp in enumerate(employees[:15], 1):
                        print(f"    {i}. {emp['name']:<40} | {emp['department']}")

        print(f"\n" + "="*120)
        print(f"SUMMARY")
        print(f"="*120)
        print(f"\nOPL Employees in July 2024: {opl_count}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
