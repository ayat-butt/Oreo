#!/usr/bin/env python3
"""Comprehensive cross-check: employees AND dependents by name or CNIC."""

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

def extract_clean_name(text):
    """Extract clean name from formatted cell."""
    if not text:
        return ""
    text = text.strip()
    text = text.replace('[EMP]', '').replace('[EMP-INCOMPLETE]', '')
    text = text.replace('└─', '').strip()
    return text.lower()

def get_main_sheet_data(service, sheet_id):
    """Get all employees and their CNICs from main sheet."""
    print("Reading Main Sheet (Column B-C for employee/CNIC data)...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!B:C'
        ).execute()

        values = result.get('values', [])
        employees_by_name = {}
        employees_by_cnic = {}

        for row in values[1:]:
            if not row or not row[0]:
                continue

            col_b = row[0].strip()  # Employee name
            col_c = row[1].strip() if len(row) > 1 else ""  # CNIC

            # Skip section headers and empty
            if not col_b or col_b.startswith('[') or col_b.startswith('=') or len(col_b) < 3:
                continue

            # Store by name
            employees_by_name[col_b.lower()] = {
                'name': col_b,
                'cnic': col_c
            }
            # Store by CNIC
            if col_c and col_c != "CNIC":
                employees_by_cnic[col_c.lower()] = {
                    'name': col_b,
                    'cnic': col_c
                }

        print(f"[OK] Found {len(employees_by_name)} employees in Main Sheet\n")
        return employees_by_name, employees_by_cnic

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

def get_old_sheet_full_data(service, sheet_id):
    """Get all records (employees and dependents) from old sheet."""
    print("Reading Old Sheet (employees and dependents)...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        values = result.get('values', [])
        all_records = []
        employee_count = 0
        dependent_count = 0

        for idx, row in enumerate(values[1:], 1):
            if not row or not row[0]:
                continue

            emp_name = row[0].strip() if row[0] else ""
            emp_cnic = row[1].strip() if len(row) > 1 else ""
            dependent_name = row[2].strip() if len(row) > 2 else ""

            if not emp_name:
                continue

            all_records.append({
                'employee_name': emp_name,
                'employee_cnic': emp_cnic,
                'dependent_name': dependent_name,
                'row_data': row,
                'row_idx': idx
            })

            if not dependent_name:
                employee_count += 1
            else:
                dependent_count += 1

        print(f"[OK] Found {len(all_records)} total records")
        print(f"     {employee_count} employee records")
        print(f"     {dependent_count} dependent records\n")

        return all_records

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return []

def fuzzy_match_name(name, target_dict, threshold=0.85):
    """Fuzzy match a name against dict of names."""
    name_lower = name.lower().strip()

    for key in target_dict.keys():
        score = SequenceMatcher(None, name_lower, key).ratio()
        if score > threshold:
            return True, score

    return False, 0.0

def cross_check(employees_by_name, employees_by_cnic, all_records):
    """Cross-check old records against main sheet."""
    print("Cross-checking employees and dependents...\n")

    missing_records = []
    found_count = 0
    missing_count = 0

    for record in all_records:
        emp_name = record['employee_name']
        emp_cnic = record['employee_cnic']
        dependent_name = record['dependent_name']

        # Try to find employee by CNIC first (most reliable)
        found_in_main = False
        match_type = ""

        if emp_cnic and emp_cnic.lower() in employees_by_cnic:
            found_in_main = True
            match_type = "CNIC match"
        elif emp_name.lower() in employees_by_name:
            found_in_main = True
            match_type = "Name exact"
        else:
            # Try fuzzy match
            fuzzy_found, score = fuzzy_match_name(emp_name, employees_by_name)
            if fuzzy_found:
                found_in_main = True
                match_type = f"Fuzzy {score:.0%}"

        if found_in_main:
            found_count += 1
            if dependent_name:
                print(f"  [FOUND] {emp_name} - Dependent: {dependent_name} ({match_type})")
            else:
                print(f"  [FOUND] {emp_name} ({match_type})")
        else:
            missing_count += 1
            missing_records.append(record)
            if dependent_name:
                print(f"  [MISSING] {emp_name} - Dependent: {dependent_name}")
            else:
                print(f"  [MISSING] {emp_name}")

    print(f"\nSummary:")
    print(f"  Found: {found_count} records")
    print(f"  Missing: {missing_count} records")

    return missing_records

def update_reference_sheet(service, sheet_id, missing_records):
    """Update reference sheet with missing records."""
    print(f"\nUpdating Reference Sheet with {len(missing_records)} missing records...")

    try:
        # Get headers
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1:J1"
        ).execute()
        headers = result.get('values', [[]])[0]

        # Build new data
        new_data = [headers]
        for record in missing_records:
            new_data.append(record['row_data'])

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

        print(f"[OK] Updated with {len(missing_records)} records\n")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 100)
    print("COMPREHENSIVE CROSS-CHECK: By Name OR CNIC (including dependents)")
    print("=" * 100 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get data
    employees_by_name, employees_by_cnic = get_main_sheet_data(service, sheet_id)
    all_records = get_old_sheet_full_data(service, sheet_id)

    if not employees_by_name or not all_records:
        print("[ERROR] Could not read sheets")
        return

    # Cross-check
    missing_records = cross_check(employees_by_name, employees_by_cnic, all_records)

    # Update
    if update_reference_sheet(service, sheet_id, missing_records):
        print("=" * 100)
        print("FINAL RESULTS")
        print("=" * 100)
        print(f"\nMain Sheet: {len(employees_by_name)} unique employees")
        print(f"Old Insurance Sheet: {len(all_records)} total records")
        print(f"\nMissing from Main Sheet: {len(missing_records)} records")
        print(f"\nReference Tab updated with {len(missing_records)} missing records")
        print("These include:")
        print("  - Employees not found in current active list")
        print("  - Dependents whose employees are not in current active list")

if __name__ == "__main__":
    main()
