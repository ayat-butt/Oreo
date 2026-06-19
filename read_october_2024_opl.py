#!/usr/bin/env python3
"""Read October 2024 specifically for OPL employees"""

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
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    # October 2024 sheet
    sheet_id = '1h1IRXwxx-mRAp0m2C2sqHlIjR5OzYpjc'

    print("="*120)
    print("READING OCTOBER 2024 FOR OPL EMPLOYEES")
    print("="*120)

    try:
        # Get metadata
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        print(f"\nSheets found in October 2024 workbook:")
        sheet_names = []
        for sheet in sheets:
            title = sheet['properties']['title']
            sheet_names.append(title)
            print(f"  - {title}")

        # Try each sheet to find OPL data
        print(f"\nSearching each sheet for OPL employees:\n")

        opl_employees = {}

        for sheet_name in sheet_names:
            try:
                result = service.spreadsheets().values().get(
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

                # Extract employees from this sheet
                sheet_employees = {}
                for row_idx in range(header_row + 1, len(rows)):
                    row = rows[row_idx]
                    if not row or len(row) < 2:
                        continue

                    name = row[name_col].strip() if name_col and name_col < len(row) else ''
                    if not name or 'total' in name.lower() or len(name) < 3:
                        continue

                    dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
                    sheet_employees[name] = dept

                if sheet_employees:
                    print(f"Sheet '{sheet_name}': Found {len(sheet_employees)} employees")
                    opl_employees.update(sheet_employees)

            except Exception as e:
                print(f"Sheet '{sheet_name}': Error - {str(e)[:80]}")
                continue

        # Summary
        print(f"\n{'='*120}")
        print(f"OCTOBER 2024 OPL EMPLOYEES SUMMARY")
        print(f"{'='*120}")
        print(f"\nTotal unique OPL employees found: {len(opl_employees)}")

        if opl_employees:
            print(f"\nOPL Employee List (October 2024):")
            print("-"*120)
            for i, (name, dept) in enumerate(sorted(opl_employees.items()), 1):
                print(f"{i:3d}. {name:<40} | Dept: {dept}")

            # Save to file
            with open('output/OCTOBER_2024_OPL_EMPLOYEES.txt', 'w', encoding='utf-8') as f:
                f.write("OCTOBER 2024 - OPL EMPLOYEES\n")
                f.write("="*80 + "\n\n")
                f.write(f"Total: {len(opl_employees)} employees\n\n")
                for name, dept in sorted(opl_employees.items()):
                    f.write(f"{name:<40} | {dept}\n")

            print(f"\nSaved to: output/OCTOBER_2024_OPL_EMPLOYEES.txt")
        else:
            print("\nNo OPL employees found in any sheet")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
