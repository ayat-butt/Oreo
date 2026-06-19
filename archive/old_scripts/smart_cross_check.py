#!/usr/bin/env python3
"""Smart cross-check - extract clean names and compare properly."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from difflib import SequenceMatcher
import re

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
        print(f"Error: {e}")
        return None

def extract_clean_name(text):
    """Extract clean employee name from formatted text."""
    if not text:
        return ""

    text = text.strip()

    # Remove [EMP], [EMP-INCOMPLETE], etc.
    text = re.sub(r'^\[EMP[^\]]*\]\s*', '', text)

    # Remove dependent indicator (└─)
    text = re.sub(r'^\s*└─\s*', '', text)

    # Remove leading/trailing spaces and hyphens
    text = text.strip(' -═')

    return text.lower()

def get_main_sheet_names(service, sheet_id):
    """Get all clean employee names from main sheet."""
    print("Reading Main Sheet...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!A:A'
        ).execute()

        values = result.get('values', [])
        names_set = set()

        for row in values[1:]:  # Skip header
            if row and row[0]:
                clean_name = extract_clean_name(row[0])

                # Filter: must be actual names (not section headers, not single words in caps)
                if clean_name and len(clean_name) > 3 and not clean_name.startswith('='):
                    names_set.add(clean_name)

        print(f"[OK] Extracted {len(names_set)} unique employee names from Main Sheet\n")
        return names_set

    except Exception as e:
        print(f"[ERROR] {e}")
        return set()

def get_reference_names_and_data(service, sheet_id):
    """Get employee names from reference sheet."""
    print("Reading Reference Sheet...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        values = result.get('values', [])
        names_data = {}

        for idx, row in enumerate(values[1:], 1):  # Skip header
            if not row or not row[0]:
                continue

            emp_name = row[0].strip()

            if emp_name and not emp_name.lower().startswith('employee'):
                name_lower = emp_name.lower()
                if name_lower not in names_data:
                    names_data[name_lower] = {
                        'original_name': emp_name,
                        'row_index': idx,
                        'data': row
                    }

        print(f"[OK] Found {len(names_data)} records in Reference Sheet\n")
        return names_data

    except Exception as e:
        print(f"[ERROR] {e}")
        return {}

def compare_and_find_missing(main_names, reference_names):
    """Find which reference names are missing from main sheet."""
    print("Comparing data...\n")

    found_count = 0
    missing_count = 0
    missing_data = {}

    for ref_name, ref_info in reference_names.items():
        # Check exact match
        if ref_name in main_names:
            found_count += 1
            print(f"  [FOUND] {ref_info['original_name']}")
        else:
            # Check fuzzy match
            best_score = 0
            for main_name in main_names:
                score = SequenceMatcher(None, ref_name, main_name).ratio()
                if score > best_score:
                    best_score = score

            if best_score < 0.80:  # Not a good match
                missing_count += 1
                missing_data[ref_name] = ref_info
                print(f"  [MISSING] {ref_info['original_name']}")
            else:
                found_count += 1
                print(f"  [FOUND] {ref_info['original_name']} (fuzzy: {best_score:.0%})")

    return found_count, missing_count, missing_data

def update_reference_sheet_clean(service, sheet_id, headers, missing_data, reference_names):
    """Update reference sheet with only truly missing employees."""
    print(f"\nUpdating Reference Sheet...")

    try:
        # Build new data with only missing employees
        new_data = [headers]

        for name, info in missing_data.items():
            new_data.append(info['data'])

        # Clear the reference sheet
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        # Write only missing data
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1",
            valueInputOption='USER_ENTERED',
            body={'values': new_data}
        ).execute()

        print(f"[OK] Updated with {len(missing_data)} missing employee records")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 100)
    print("SMART CROSS-CHECK: Reference Tab vs Main Sheet")
    print("=" * 100 + "\n")

    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not authenticate")
        return

    service = build('sheets', 'v4', credentials=creds)
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get main sheet names
    main_names = get_main_sheet_names(service, sheet_id)

    # Get reference data
    reference_data = get_reference_names_and_data(service, sheet_id)

    if not reference_data:
        print("[ERROR] Reference sheet is empty")
        return

    # Get headers
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1:J1"
        ).execute()
        headers = result.get('values', [[]])[0]
    except:
        headers = ['Employee Name', 'CNIC', 'Dependent', 'Relationship', 'DOB', 'Health Plan', 'Life Plan', 'OPD Plan', 'Date Added', 'Notes']

    # Compare
    found, missing, missing_data = compare_and_find_missing(main_names, reference_data)

    # Update sheet
    if update_reference_sheet_clean(service, sheet_id, headers, missing_data, reference_data):
        print("\n" + "=" * 100)
        print("RESULTS")
        print("=" * 100)
        print(f"\nMain Sheet has: {len(main_names)} unique employee names")
        print(f"Old Sheet has: {len(reference_data)} records")
        print(f"\nFound in Main Sheet: {found}")
        print(f"MISSING (kept in Reference): {missing}")
        print(f"\nReference Tab now contains ONLY employees from old sheet who are NOT in Main Sheet")
        print(f"These {missing} records need your attention!")
    else:
        print("[ERROR] Could not update")

if __name__ == "__main__":
    main()
