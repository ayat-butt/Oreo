#!/usr/bin/env python3
"""Proper cross-check by reading both sheets completely."""

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

def get_main_sheet_data(service, sheet_id):
    """Read main sheet data more carefully."""
    print("Reading Main Sheet (columns A-C for names)...")
    try:
        # Read first 3 columns to get name data
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!A1:C300'
        ).execute()

        values = result.get('values', [])

        # Extract employee names more carefully
        main_employees = {}

        for row in values[1:]:  # Skip header
            if not row:
                continue

            col_a = row[0].strip() if row[0] else ""
            col_b = row[1].strip() if len(row) > 1 and row[1] else ""

            # Skip empty rows and section headers
            if not col_a or col_a.startswith('=') or len(col_a) < 3:
                continue

            # Extract name from col A (remove [EMP] and spacing)
            clean_name = col_a
            clean_name = re.sub(r'^\[EMP[^\]]*\]\s*', '', clean_name)  # Remove [EMP...] prefix
            clean_name = re.sub(r'^\s*└─\s*', '', clean_name)  # Remove dependent marker
            clean_name = clean_name.strip()

            # If it's a real employee name (not a section header or separator)
            if clean_name and len(clean_name) > 3 and not clean_name.isupper():
                name_key = clean_name.lower()
                main_employees[name_key] = {
                    'display_name': clean_name,
                    'employee_id': col_b,
                    'col_a': col_a
                }
            # Try uppercase names too (some are in all caps)
            elif clean_name and len(clean_name) > 3 and clean_name.isupper():
                name_key = clean_name.lower()
                main_employees[name_key] = {
                    'display_name': clean_name,
                    'employee_id': col_b,
                    'col_a': col_a
                }

        print(f"[OK] Extracted {len(main_employees)} employee names from Main Sheet\n")

        # Show sample
        if main_employees:
            print("Sample employee names from Main Sheet:")
            for i, (key, data) in enumerate(list(main_employees.items())[:5]):
                print(f"  - {data['display_name']} | ID: {data['employee_id']}")
            print()

        return main_employees

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return {}

def get_old_sheet_data(service, sheet_id):
    """Read old sheet data."""
    print("Reading Old Sheet (Reference Tab)...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        values = result.get('values', [])
        old_employees = {}

        for idx, row in enumerate(values[1:], 1):  # Skip header
            if not row or not row[0]:
                continue

            emp_name = row[0].strip()

            if emp_name:
                name_key = emp_name.lower()
                old_employees[name_key] = {
                    'display_name': emp_name,
                    'row_index': idx,
                    'data': row
                }

        print(f"[OK] Extracted {len(old_employees)} employee names from Old Sheet\n")

        # Show sample
        if old_employees:
            print("Sample employee names from Old Sheet:")
            for i, (key, data) in enumerate(list(old_employees.items())[:5]):
                print(f"  - {data['display_name']}")
            print()

        return old_employees

    except Exception as e:
        print(f"[ERROR] {e}")
        return {}

def match_names(main_employees, old_employees):
    """Match old sheet employees with main sheet."""
    print("Matching employees...\n")

    found = []
    missing = []

    for old_key, old_data in old_employees.items():
        old_name = old_data['display_name']

        # Try exact match (case-insensitive)
        if old_key in main_employees:
            found.append({
                'old_name': old_name,
                'main_name': main_employees[old_key]['display_name'],
                'match_type': 'exact',
                'confidence': 1.0
            })
        else:
            # Try fuzzy match
            best_match = None
            best_score = 0

            for main_key, main_data in main_employees.items():
                score = SequenceMatcher(None, old_key, main_key).ratio()
                if score > best_score and score > 0.85:
                    best_score = score
                    best_match = main_data

            if best_match:
                found.append({
                    'old_name': old_name,
                    'main_name': best_match['display_name'],
                    'match_type': f'fuzzy',
                    'confidence': best_score
                })
            else:
                missing.append({
                    'old_name': old_name,
                    'row_data': old_data['data']
                })

    return found, missing

def main():
    print("\n" + "=" * 100)
    print("PROPER CROSS-CHECK - DETAILED ANALYSIS")
    print("=" * 100 + "\n")

    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not authenticate")
        return

    service = build('sheets', 'v4', credentials=creds)
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get both sheets
    main_employees = get_main_sheet_data(service, sheet_id)
    old_employees = get_old_sheet_data(service, sheet_id)

    if not main_employees or not old_employees:
        print("[ERROR] Could not read sheets properly")
        return

    # Match
    found, missing = match_names(main_employees, old_employees)

    print("\n" + "=" * 100)
    print("DETAILED RESULTS")
    print("=" * 100)

    print(f"\nMain Sheet: {len(main_employees)} employees")
    print(f"Old Sheet: {len(old_employees)} employees")
    print(f"\nMatched (FOUND in Main Sheet): {len(found)}")
    print(f"Not Matched (MISSING from Main Sheet): {len(missing)}")

    if found:
        print(f"\n--- FOUND IN MAIN SHEET ({len(found)}) ---")
        for match in found[:10]:
            print(f"  ✓ {match['old_name']:<40} → {match['main_name']:<40} ({match['match_type']})")
        if len(found) > 10:
            print(f"  ... and {len(found) - 10} more")

    if missing:
        print(f"\n--- MISSING FROM MAIN SHEET ({len(missing)}) ---")
        for miss in missing[:10]:
            print(f"  ✗ {miss['old_name']:<40}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

    print("\n" + "=" * 100)
    print("NEXT STEP: Do you want me to update the Reference Tab to keep ONLY these")
    print(f"{len(missing)} truly missing employees?")
    print("=" * 100)

if __name__ == "__main__":
    main()
