#!/usr/bin/env python3
"""Cross-check current Markaz with previous year's insurance sheet."""

import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

def load_google_credentials():
    """Load Google credentials."""
    token_path = 'c:/Agent Oreo/token.json'
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def read_old_insurance_sheet():
    """Read the previous year's insurance sheet."""
    print("Loading Google Sheets credentials...")
    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not authenticate")
        return None

    service = build('sheets', 'v4', credentials=creds)

    # Old insurance sheet ID from user's URL
    old_sheet_id = '1HjyeoWzsxkC_t2yzPgSn6qb_huvNYq7qvzHB2m-AxHI'

    print(f"Reading old insurance sheet...")
    try:
        # First get sheet metadata to find sheet names
        metadata = service.spreadsheets().get(spreadsheetId=old_sheet_id).execute()
        sheets = metadata.get('sheets', [])
        print(f"\nAvailable sheets in old insurance file:")
        for sheet in sheets:
            print(f"  - {sheet['properties']['title']} (gid: {sheet['properties']['sheetId']})")

        # Try to read from the first sheet or the one with gid=195402472
        sheet_name = None
        for sheet in sheets:
            if sheet['properties']['sheetId'] == 195402472:
                sheet_name = sheet['properties']['title']
                break

        if not sheet_name:
            sheet_name = sheets[0]['properties']['title'] if sheets else 'Sheet1'

        print(f"\nReading from sheet: '{sheet_name}'")

        # Read the data
        result = service.spreadsheets().values().get(
            spreadsheetId=old_sheet_id,
            range=f'{sheet_name}'
        ).execute()

        values = result.get('values', [])
        print(f"[OK] Read {len(values)} rows from old sheet")

        return values
    except Exception as e:
        print(f"[ERROR] Could not read old sheet: {e}")
        return None

def parse_old_sheet(values):
    """Parse the old insurance sheet data."""
    if not values or len(values) < 2:
        print("[ERROR] Old sheet is empty or has no data")
        return {}

    # Find header row
    headers = values[0]
    print(f"\nHeaders from old sheet: {headers}\n")

    # Parse employee data based on actual columns
    old_employees = {}
    for row_idx, row in enumerate(values[1:], 1):
        if not row or len(row) < 1:
            continue

        # Extract data based on column positions
        emp_name = row[0] if len(row) > 0 else None
        cnic = row[1] if len(row) > 1 else None
        insured_name = row[2] if len(row) > 2 else None
        relation = row[3] if len(row) > 3 else None
        dob = row[4] if len(row) > 4 else None
        health_plan = row[5] if len(row) > 5 else None
        life_plan = row[6] if len(row) > 6 else None
        opd_plan = row[7] if len(row) > 7 else None
        date_added = row[9] if len(row) > 9 else None

        if emp_name and emp_name.strip():
            emp_key = emp_name.strip()
            if emp_key not in old_employees:
                old_employees[emp_key] = {
                    'name': emp_name,
                    'cnic': cnic,
                    'dependents': []
                }

            # Add dependent info if it's a dependent entry
            if insured_name and insured_name != emp_name:
                old_employees[emp_key]['dependents'].append({
                    'name': insured_name,
                    'relation': relation,
                    'dob': dob
                })

    print(f"[OK] Parsed {len(old_employees)} employees from old sheet")
    return old_employees

def main():
    print("\n" + "=" * 100)
    print("CROSS-CHECK: OLD INSURANCE SHEET vs CURRENT MARKAZ")
    print("=" * 100)

    # Read old sheet
    print("\n[Step 1] Reading previous year's insurance sheet...")
    old_values = read_old_insurance_sheet()

    if not old_values:
        print("[ERROR] Could not read old sheet. Please check the URL and try again.")
        return

    print("\n[Step 2] Parsing old sheet data...")
    old_employees = parse_old_sheet(old_values)

    if not old_employees:
        print("[ERROR] No employee data found in old sheet")
        return

    print("\n" + "=" * 100)
    print(f"OLD SHEET SUMMARY: {len(old_employees)} employees found")
    print("=" * 100)

    print("\nSample employees from old sheet (first 5):")
    for i, (emp_name, emp_data) in enumerate(list(old_employees.items())[:5], 1):
        print(f"{i}. Name: {emp_name}")
        if emp_data.get('cnic'):
            print(f"   CNIC: {emp_data['cnic']}")
        if emp_data.get('dependents'):
            print(f"   Dependents: {len(emp_data['dependents'])}")
            for dep in emp_data['dependents'][:2]:
                print(f"     - {dep['name']} ({dep['relation']})")
        print()

    print("=" * 100)
    print("NOTE: To complete the cross-check, I need to:")
    print("  1. Compare employee IDs between old and new sheets")
    print("  2. Identify missing employees")
    print("  3. Identify missing data (CNIC, DOB, Bank, etc.)")
    print("  4. Generate detailed report")
    print("\nPlease confirm if you want me to proceed with the full analysis.")
    print("=" * 100)

if __name__ == "__main__":
    main()
