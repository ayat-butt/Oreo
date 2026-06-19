#!/usr/bin/env python3
"""Read all provided sheets and extract OPL employee data"""

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

def get_sheet_data(service, sheet_id, label):
    """Fetch data from a sheet"""
    try:
        print(f"\n{label}...", end='')

        # Get metadata to find sheet names
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = metadata.get('sheets', [])

        if not sheets:
            print(" No sheets found")
            return {}

        # Try to find OPL sheet or first available
        opl_sheet_name = None
        for sheet in sheets:
            title = sheet['properties']['title']
            if 'OPL' in title.upper():
                opl_sheet_name = title
                break

        if not opl_sheet_name:
            opl_sheet_name = sheets[0]['properties']['title']

        # Fetch data
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{opl_sheet_name}'!A1:Z500"
        ).execute()

        rows = result.get('values', [])

        # Find header
        header_row = None
        for i, row in enumerate(rows[:15]):
            if row and any('employee' in str(cell).lower() for cell in row):
                header_row = i
                break

        if header_row is None:
            print(" No employee data found")
            return {}

        headers = rows[header_row]
        name_col = None
        dept_col = None
        designation_col = None

        for col_idx, header in enumerate(headers):
            h = str(header).lower()
            if 'employee' in h and name_col is None:
                name_col = col_idx
            elif 'depart' in h:
                dept_col = col_idx
            elif 'designation' in h:
                designation_col = col_idx

        # Extract employees
        employees = {}
        for row_idx in range(header_row + 1, len(rows)):
            row = rows[row_idx]
            if not row or len(row) < 2:
                continue

            name = row[name_col].strip() if name_col and name_col < len(row) else ''
            if not name or 'total' in name.lower() or len(name) < 3:
                continue

            dept = row[dept_col].strip() if dept_col and dept_col < len(row) else ''
            designation = row[designation_col].strip() if designation_col and designation_col < len(row) else ''

            employees[name] = {
                'department': dept,
                'designation': designation
            }

        print(f" Found {len(employees)} employees in '{opl_sheet_name}'")
        return employees

    except Exception as e:
        print(f" Error: {e}")
        return {}

def main():
    creds = load_credentials()
    if not creds:
        print("Failed to load credentials")
        return

    service = build('sheets', 'v4', credentials=creds)

    # All sheet IDs from user
    sheets_to_read = {
        '1NLyPSfEO7N92EjGIBy6EnrrjvWmE7QTi': 'Sheet 1',
        '1jBlbB-Ff54udES4o_G_-qhB8aAuW53Hb1jRlGNDmZ3E': 'Sheet 2',
        '1IklN-MJqHjKlXI6s1B3I58_JGnOi0I0tEoO0rf3wkwY': 'Sheet 3',
        '1Fi_BVfQAwDi5tSPhvRWK6dPSgCOPVYoBOhNQ81zcTBI': 'Sheet 4',
        '1wdTogupsdtkcOEXgQWNwsiJNnUOwx-87JYcpv6MSop4': 'Sheet 5',
        '1_A5o1Aln9AjEmjX-BzXyWfHdzLajYvwiRVmRtiKH4hs': 'Sheet 6',
        '14rfFm49DNyESepj5Lfux1OG1QYbv5QtDTUXYh1FuNUU': 'Sheet 7',
        '1e83npqk4HQmm0_ELlbdqJFZDXwbkz94V4RGUjpdOzE0': 'Sheet 8',
        '1ahND0ab4mIOe1_dduUt-2tuxKvdugoEyNd2qh8HV5TQ': 'Sheet 9',
        '1cENuT5O49O5f-ut621XlJqQ0yWFni0x6G8TNAzK6hzU': 'Sheet 10',
        '1drSWY44h-INF3aE6TIvrqT-MFuXc1DTLoWrFMBXxUNU': 'Sheet 11',
        '1C6sZRGVqvLrt5kKMx7jwIw7EoI4tbgHeqpmohScPXIo': 'Sheet 12',
    }

    print("="*120)
    print("READING ALL PROVIDED SHEETS FOR OPL DATA")
    print("="*120)

    all_sheet_employees = {}
    for sheet_id, label in sheets_to_read.items():
        employees = get_sheet_data(service, sheet_id, label)
        all_sheet_employees[label] = employees

    # Summary
    print("\n" + "="*120)
    print("SUMMARY")
    print("="*120)

    total_unique = set()
    for label, employees in all_sheet_employees.items():
        if employees:
            print(f"{label}: {len(employees)} employees")
            total_unique.update(employees.keys())
        else:
            print(f"{label}: No data")

    print(f"\nTotal unique employees across all sheets: {len(total_unique)}")
    print("\nFull employee list:")
    for name in sorted(total_unique):
        print(f"  - {name}")

if __name__ == '__main__':
    main()
