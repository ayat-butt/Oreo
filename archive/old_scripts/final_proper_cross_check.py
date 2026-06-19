#!/usr/bin/env python3
"""Final proper cross-check using Column B for employee names."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from difflib import SequenceMatcher

def load_google_credentials():
    token_path = 'c:/Agent Oreo/token.json'
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_main_sheet_names(service, sheet_id):
    """Get employee names from Column B of main sheet."""
    print("Reading Main Sheet (Column B)...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!B:B'
        ).execute()

        values = result.get('values', [])
        names_set = set()
        names_list = []

        for row in values[1:]:  # Skip header
            if row and row[0]:
                name = row[0].strip()

                # Skip section headers and empty
                if name and name != 'OPL' and name != 'OWT' and len(name) > 2 and not name.startswith('['):
                    names_set.add(name.lower())
                    names_list.append(name)

        print(f"[OK] Found {len(names_set)} unique employee names in Main Sheet\n")

        # Show samples
        if names_list:
            print("Sample names from Main Sheet:")
            for name in names_list[1:6]:
                try:
                    print(f"  - {name}")
                except UnicodeEncodeError:
                    print(f"  - [Non-ASCII name]")
            print()

        return names_set, names_list

    except Exception as e:
        print(f"[ERROR] {e}")
        return set(), []

def get_old_sheet_employees(service, sheet_id):
    """Get employees from old sheet."""
    print("Reading Old Sheet (Reference Tab)...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        values = result.get('values', [])
        employees = {}

        for idx, row in enumerate(values[1:], 1):
            if not row or not row[0]:
                continue

            emp_name = row[0].strip()

            if emp_name:
                name_lower = emp_name.lower()
                employees[name_lower] = {
                    'original_name': emp_name,
                    'row_index': idx,
                    'data': row
                }

        print(f"[OK] Found {len(employees)} unique employees in Old Sheet\n")

        if employees:
            print("Sample names from Old Sheet:")
            for i, (key, data) in enumerate(list(employees.items())[:5]):
                print(f"  - {data['original_name']}")
            print()

        return employees

    except Exception as e:
        print(f"[ERROR] {e}")
        return {}

def cross_check(main_names_set, main_names_list, old_employees):
    """Cross-check and find truly missing employees."""
    print("Cross-checking...\n")

    found_count = 0
    missing_employees = {}

    for old_name_lower, old_info in old_employees.items():
        old_name = old_info['original_name']

        # Exact match
        if old_name_lower in main_names_set:
            found_count += 1
            print(f"  [FOUND] {old_name}")
        else:
            # Fuzzy match
            best_score = 0
            for main_name in main_names_list:
                score = SequenceMatcher(None, old_name_lower, main_name.lower()).ratio()
                if score > best_score:
                    best_score = score

            if best_score < 0.80:  # Not a good match
                missing_employees[old_name_lower] = old_info
                print(f"  [MISSING] {old_name}")
            else:
                found_count += 1
                print(f"  [FOUND] {old_name} (fuzzy: {best_score:.0%})")

    return found_count, missing_employees

def update_reference_sheet(service, sheet_id, missing_employees):
    """Update reference sheet with only missing employees."""
    print(f"\nUpdating Reference Sheet...")

    try:
        # Get headers
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1:J1"
        ).execute()
        headers = result.get('values', [[]])[0]

        # Build new data
        new_data = [headers]
        for name_lower, emp_info in missing_employees.items():
            new_data.append(emp_info['data'])

        # Clear and update
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1",
            valueInputOption='USER_ENTERED',
            body={'values': new_data}
        ).execute()

        print(f"[OK] Updated with {len(missing_employees)} truly missing employees\n")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 100)
    print("FINAL CROSS-CHECK: Old Sheet vs Main Sheet (Proper)")
    print("=" * 100 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get main sheet names from Column B
    main_names_set, main_names_list = get_main_sheet_names(service, sheet_id)

    # Get old sheet employees
    old_employees = get_old_sheet_employees(service, sheet_id)

    if not main_names_set or not old_employees:
        print("[ERROR] Could not read sheets")
        return

    # Cross-check
    found, missing = cross_check(main_names_set, main_names_list, old_employees)

    # Update sheet
    if update_reference_sheet(service, sheet_id, missing):
        print("=" * 100)
        print("FINAL RESULTS")
        print("=" * 100)
        print(f"\nMain Sheet: {len(main_names_set)} unique employees")
        print(f"Old Sheet: {len(old_employees)} employees")
        print(f"\nFound in Main Sheet: {found}")
        print(f"Missing from Main Sheet: {len(missing)}")
        print(f"\nReference Tab updated: Now contains ONLY {len(missing)} employees not found in Main Sheet")
        print("\nThese are the employees who:")
        print("  - Left the company (not in current active list)")
        print("  - Changed names (couldn't be matched)")
        print("  - May need to be re-added with new data")

if __name__ == "__main__":
    main()
