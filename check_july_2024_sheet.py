#!/usr/bin/env python3
"""Check July 2024 sheet for OPL employees"""

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

    service = build('sheets', 'v4', credentials=creds)

    # July 2024 sheet ID from the user
    sheet_id = '1NLyPSfEO7N92EjGIBy6EnrrjvWmE7QTi'

    print("="*120)
    print("ANALYZING JULY 2024 SHEET")
    print("="*120)

    try:
        # Get metadata
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets found in workbook: {len(sheets)}")
        sheet_names = []
        for sheet in sheets:
            title = sheet['properties']['title']
            sheet_names.append(title)
            print(f"  - {title}")

        # Look for OPL sheet
        print(f"\nSearching for OPL sheet...\n")

        for sheet_name in sheet_names:
            print(f"Reading sheet: '{sheet_name}'")

            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=f"'{sheet_name}'!A1:Z500"
                ).execute()

                rows = result.get('values', [])
                print(f"  Total rows: {len(rows)}")

                if not rows:
                    print(f"  Empty sheet\n")
                    continue

                # Find header row
                header_row = None
                for i, row in enumerate(rows[:15]):
                    if row and any('employee' in str(cell).lower() for cell in row):
                        header_row = i
                        break

                if header_row is None:
                    print(f"  No employee header found\n")
                    continue

                print(f"  Header row: {header_row}")
                print(f"  Headers: {rows[header_row][:10]}")

                # Extract employees
                headers = rows[header_row]
                name_col = None
                dept_col = None

                for col_idx, header in enumerate(headers):
                    h = str(header).lower()
                    if 'employee' in h and name_col is None:
                        name_col = col_idx
                    elif 'depart' in h:
                        dept_col = col_idx

                employees = []
                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if not row or len(row) < 2:
                        continue

                    name = str(row[name_col]).strip() if name_col and name_col < len(row) else ''
                    if not name or 'total' in name.lower() or len(name) < 3:
                        continue

                    dept = str(row[dept_col]).strip() if dept_col and dept_col < len(row) else ''
                    employees.append({'name': name, 'department': dept})

                if employees:
                    print(f"  Found {len(employees)} employees in this sheet")
                    print(f"\n  First 10 employees:")
                    for i, emp in enumerate(employees[:10], 1):
                        print(f"    {i}. {emp['name']} - {emp['department']}")
                    print(f"\n")

            except Exception as e:
                print(f"  Error: {str(e)[:100]}\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
