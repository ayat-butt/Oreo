#!/usr/bin/env python3
"""Count employees in April 2025 OPL sheet - from 'Employee' column"""

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

def main():
    creds = load_credentials()
    if not creds:
        return

    sheets_service = build('sheets', 'v4', credentials=creds)

    # April 2025 sheet
    sheet_id = '1cENuT5O49O5f-ut621XlJqQ0yWFni0x6G8TNAzK6hzU'

    print("="*120)
    print("APRIL 2025 - COUNTING EMPLOYEES FROM 'EMPLOYEE' COLUMN IN OPL SHEET")
    print("="*120)

    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets in workbook: {len(sheets)}")
        for i, sheet in enumerate(sheets):
            title = sheet['properties']['title']
            print(f"  {i+1}. '{title}'")

        # Find and read OPL sheet
        opl_sheet = None
        for sheet in sheets:
            if sheet['properties']['title'].upper() == 'OPL':
                opl_sheet = sheet
                break

        if opl_sheet is None:
            print("\nNo OPL sheet found!")
            return

        sheet_name = opl_sheet['properties']['title']
        print(f"\nReading OPL sheet: '{sheet_name}'")

        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!A1:Z1000"
        ).execute()

        rows = result.get('values', [])
        print(f"  Total rows: {len(rows)}")

        # Find header row
        header_row = None
        for i, row in enumerate(rows[:15]):
            if row and any(cell for cell in row):
                header_row = i
                break

        if header_row is None:
            print("  No header row found")
            return

        headers = rows[header_row]
        print(f"  Headers (first 10): {headers[:10]}")

        # Find "Employee" column (not "Employee ID")
        employees_col = None
        for col_idx, header in enumerate(headers):
            h = str(header).lower().strip()
            if h == 'employee':
                employees_col = col_idx
                print(f"  Found Employee column at index {col_idx}: '{header}'")
                break

        if employees_col is None:
            print("  'Employee' column not found!")
            return

        # Count entries in Employee column
        count = 0
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if not row or len(row) <= employees_col:
                continue

            employee = str(row[employees_col]).strip() if employees_col < len(row) else ''
            if not employee:
                continue

            if 'total' in employee.lower():
                continue

            if len(employee) >= 2:
                count += 1

        print(f"\n  Total employees in 'Employee' column: {count}")

        print(f"\n{'='*120}")
        print(f"TOTAL OPL EMPLOYEES IN APRIL 2025: {count}")
        print(f"{'='*120}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
