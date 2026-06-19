#!/usr/bin/env python3
"""Cross-check reference tab with main sheet, keep only missing data."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from difflib import SequenceMatcher

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

def get_main_sheet_employees(service, sheet_id):
    """Get all employee names from main sheet."""
    print("Reading Main Sheet employees...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!A:A'
        ).execute()

        values = result.get('values', [])
        employees = []

        for row in values[1:]:  # Skip header
            if row and row[0]:
                name = row[0].strip()
                # Skip section headers and separators
                if not name.startswith('[') and not name.startswith('=') and len(name) > 3:
                    employees.append(name.lower())

        print(f"[OK] Found {len(employees)} employees in Main Sheet\n")
        return set(employees)

    except Exception as e:
        print(f"[ERROR] {e}")
        return set()

def get_reference_sheet_data(service, sheet_id):
    """Get all data from reference sheet."""
    print("Reading Reference Sheet...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        values = result.get('values', [])
        print(f"[OK] Found {len(values)} rows in Reference Sheet (including header)\n")
        return values

    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def fuzzy_match(name, main_employees, threshold=0.85):
    """Check if name exists in main sheet with fuzzy matching."""
    name_lower = name.lower().strip()

    # Exact match
    if name_lower in main_employees:
        return True, "exact"

    # Fuzzy match
    for emp in main_employees:
        score = SequenceMatcher(None, name_lower, emp).ratio()
        if score > threshold:
            return True, f"fuzzy({score:.0%})"

    return False, "not_found"

def cross_check_and_clean(service, sheet_id, main_employees, reference_data):
    """Cross-check and identify missing employees."""
    print("Cross-checking data...")

    headers = reference_data[0] if reference_data else []
    missing_rows = [headers]  # Start with header
    duplicate_count = 0
    missing_count = 0

    for row in reference_data[1:]:
        if not row:
            continue

        emp_name = row[0].strip() if row[0] else ""

        if not emp_name or emp_name.lower().startswith('employee'):
            continue

        exists, match_type = fuzzy_match(emp_name, main_employees)

        if exists:
            duplicate_count += 1
            print(f"  [FOUND IN MAIN] {emp_name} ({match_type})")
        else:
            missing_count += 1
            print(f"  [MISSING] {emp_name}")
            missing_rows.append(row)

    print(f"\nResults:")
    print(f"  Found in Main Sheet: {duplicate_count}")
    print(f"  MISSING (to keep): {missing_count}\n")

    return missing_rows

def update_reference_sheet(service, sheet_id, missing_rows):
    """Update reference sheet with only missing data."""
    print("Updating Reference Sheet...")

    try:
        # Clear the reference sheet
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A:J"
        ).execute()

        print("[OK] Cleared old data")

        # Write only missing data
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1",
            valueInputOption='USER_ENTERED',
            body={'values': missing_rows}
        ).execute()

        print(f"[OK] Written {len(missing_rows)-1} missing records")

        # Get new sheet ID for formatting
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        new_sheet_id = None
        for sheet in metadata.get('sheets', []):
            if sheet['properties']['title'] == 'Data from Old Insurance Sheet':
                new_sheet_id = sheet['properties']['sheetId']
                break

        if new_sheet_id is not None:
            # Format header
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': new_sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.8, 'green': 0.6, 'blue': 0.2},
                                'textFormat': {
                                    'bold': True,
                                    'fontSize': 11,
                                    'foregroundColor': {'red': 0, 'green': 0, 'blue': 0}
                                },
                                'horizontalAlignment': 'CENTER'
                            }
                        },
                        'fields': 'userEnteredFormat'
                    }
                },
                {
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': new_sheet_id,
                            'gridProperties': {'frozenRowCount': 1}
                        },
                        'fields': 'gridProperties.frozenRowCount'
                    }
                }
            ]

            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()

            # Auto-resize
            requests = [{
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': new_sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 10
                    }
                }
            }]

            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()

            print("[OK] Formatting applied")

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 100)
    print("CROSS-CHECK REFERENCE TAB WITH MAIN SHEET")
    print("=" * 100 + "\n")

    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not authenticate")
        return

    service = build('sheets', 'v4', credentials=creds)
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Get main sheet employees
    main_employees = get_main_sheet_employees(service, sheet_id)

    # Get reference sheet data
    reference_data = get_reference_sheet_data(service, sheet_id)

    if not reference_data:
        print("[ERROR] Reference sheet is empty")
        return

    # Cross-check
    missing_rows = cross_check_and_clean(service, sheet_id, main_employees, reference_data)

    # Update reference sheet
    if update_reference_sheet(service, sheet_id, missing_rows):
        print("\n" + "=" * 100)
        print("SUCCESS!")
        print("=" * 100)
        print(f"\nReference Sheet Updated:")
        print(f"  Original records: {len(reference_data) - 1}")
        print(f"  Removed (found in Main Sheet): {(len(reference_data) - 1) - (len(missing_rows) - 1)}")
        print(f"  Kept (MISSING from Main Sheet): {len(missing_rows) - 1}")
        print(f"\nReference Tab now contains ONLY employees from old sheet who are NOT in Main Sheet")
        print(f"These are the employees you need to investigate further!")
    else:
        print("[ERROR] Could not update reference sheet")

if __name__ == "__main__":
    main()
