#!/usr/bin/env python3
"""Comprehensive cross-check: Old Insurance Data vs 2026 Markaz Data."""

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

def get_markaz_2026_data(service, sheet_id):
    """Get 2026 employee data from Markaz (Column B-C)."""
    print("Reading 2026 Markaz Data...")
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

            emp_name = row[0].strip()
            emp_cnic = row[1].strip() if len(row) > 1 else ""

            # Skip headers and invalid entries
            if emp_name.startswith('[') or emp_name.startswith('=') or len(emp_name) < 2:
                continue
            if emp_name.lower() in ['employee name', 'cnic']:
                continue

            # Store by name
            employees_by_name[emp_name.lower()] = {
                'name': emp_name,
                'cnic': emp_cnic
            }
            # Store by CNIC
            if emp_cnic and emp_cnic.lower() != 'cnic':
                employees_by_cnic[emp_cnic.lower()] = {
                    'name': emp_name,
                    'cnic': emp_cnic
                }

        print(f"[OK] Found {len(employees_by_name)} employees in 2026 Markaz data\n")
        return employees_by_name, employees_by_cnic

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

def get_old_insurance_data(service):
    """Get old insurance data from provided sheet."""
    print("Reading Old Insurance Data (last year)...")
    try:
        old_sheet_id = '1HjyeoWzsxkC_t2yzPgSn6qb_huvNYq7qvzHB2m-AxHI'

        result = service.spreadsheets().values().get(
            spreadsheetId=old_sheet_id,
            range="'Orenda updated data'!A:J"
        ).execute()

        values = result.get('values', [])
        all_records = []
        unique_employees = set()

        for idx, row in enumerate(values[1:], 1):
            if not row or not row[0]:
                continue

            emp_name = row[0].strip() if row[0] else ""
            emp_cnic = row[1].strip() if len(row) > 1 else ""
            insured_person = row[2].strip() if len(row) > 2 else ""
            relation = row[3].strip() if len(row) > 3 else ""

            if not emp_name:
                continue

            all_records.append({
                'employee_name': emp_name,
                'employee_cnic': emp_cnic,
                'insured_person': insured_person,
                'relation': relation,
                'row_data': row,
                'row_idx': idx
            })

            unique_employees.add(emp_name.lower())

        print(f"[OK] Found {len(all_records)} total records from old insurance")
        print(f"     Unique employees: {len(unique_employees)}\n")

        return all_records, unique_employees

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return [], set()

def fuzzy_match_name(name, target_dict, threshold=0.85):
    """Fuzzy match a name."""
    name_lower = name.lower().strip()

    for key in target_dict.keys():
        score = SequenceMatcher(None, name_lower, key).ratio()
        if score > threshold:
            return True, score

    return False, 0.0

def cross_check(employees_by_name, employees_by_cnic, old_records):
    """Cross-check old records against 2026 data."""
    print("Cross-checking employees and dependents...\n")

    missing_records = []
    found_employees = {}
    missing_employees_set = set()

    for record in old_records:
        emp_name = record['employee_name']
        emp_cnic = record['employee_cnic']
        insured_person = record['insured_person']
        relation = record['relation']

        # Try to find employee by CNIC first
        found_in_2026 = False
        match_type = ""

        if emp_cnic and emp_cnic.lower() in employees_by_cnic:
            found_in_2026 = True
            match_type = "CNIC"
        elif emp_name.lower() in employees_by_name:
            found_in_2026 = True
            match_type = "Name exact"
        else:
            # Try fuzzy match
            fuzzy_found, score = fuzzy_match_name(emp_name, employees_by_name)
            if fuzzy_found:
                found_in_2026 = True
                match_type = f"Fuzzy {score:.0%}"

        if found_in_2026:
            # Employee found in 2026
            if emp_name not in found_employees:
                found_employees[emp_name] = []
            found_employees[emp_name].append({
                'insured': insured_person,
                'relation': relation,
                'match': match_type
            })
            try:
                print(f"  [FOUND] {emp_name} ({match_type})")
                if insured_person != emp_name and relation != 'Self':
                    print(f"          - Dependent: {insured_person} ({relation})")
            except UnicodeEncodeError:
                print(f"  [FOUND] (non-ASCII name) ({match_type})")
        else:
            # Employee NOT found in 2026
            missing_records.append(record)
            missing_employees_set.add(emp_name)
            try:
                print(f"  [MISSING EMPLOYEE] {emp_name}")
                if insured_person != emp_name and relation != 'Self':
                    print(f"                    - Dependent: {insured_person} ({relation})")
                else:
                    print(f"                    - Self")
            except UnicodeEncodeError:
                print(f"  [MISSING EMPLOYEE] (non-ASCII name)")

    print(f"\n{'='*100}")
    print(f"Summary:")
    print(f"  Employees found in 2026: {len(found_employees)}")
    print(f"  Employees MISSING from 2026: {len(missing_employees_set)}")
    print(f"  Total records to keep (missing): {len(missing_records)}")

    return missing_records

def update_reference_sheet(service, sheet_id, missing_records):
    """Update reference sheet with missing records."""
    print(f"\nUpdating Reference Sheet with {len(missing_records)} missing records...")

    try:
        # Create headers matching old insurance format
        headers = ['Employee Name', 'CNIC', 'Insured Person Name', 'Relation', 'DOB',
                  'Health insurance Plan category', 'Life insurance Plan category', 'OPD Plan',
                  'App Register', 'Date of Addition']

        # Build new data
        new_data = [headers]
        for record in missing_records:
            new_data.append(record['row_data'])

        # Clear old reference tab
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        # Update with missing data
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1",
            valueInputOption='USER_ENTERED',
            body={'values': new_data}
        ).execute()

        print(f"[OK] Updated with {len(missing_records)} missing records\n")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 100)
    print("FINAL COMPREHENSIVE CROSS-CHECK")
    print("Old Insurance Data (Last Year) vs 2026 Markaz Data")
    print("=" * 100 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    markaz_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get 2026 data
    employees_by_name, employees_by_cnic = get_markaz_2026_data(service, markaz_sheet_id)

    # Get old insurance data
    old_records, unique_old_employees = get_old_insurance_data(service)

    if not employees_by_name or not old_records:
        print("[ERROR] Could not read sheets")
        return

    # Cross-check
    missing_records = cross_check(employees_by_name, employees_by_cnic, old_records)

    # Update reference tab
    if update_reference_sheet(service, markaz_sheet_id, missing_records):
        print("=" * 100)
        print("FINAL RESULTS")
        print("=" * 100)
        print(f"\n2026 Markaz Data: {len(employees_by_name)} employees")
        print(f"Old Insurance Data: {len(old_records)} total records ({len(unique_old_employees)} unique employees)")
        print(f"\nMissing from 2026 Data: {len(missing_records)} records")
        print(f"\nReference Tab ('Data from Old Insurance Sheet') updated with:")
        print(f"  - Employees not in 2026 active list")
        print(f"  - All their corresponding dependents")
        print(f"\nThese {len(missing_records)} records need your investigation:")
        print(f"  - Have they left the company?")
        print(f"  - Did they change names?")
        print(f"  - Do they need to be added back with updated data?")

if __name__ == "__main__":
    main()
