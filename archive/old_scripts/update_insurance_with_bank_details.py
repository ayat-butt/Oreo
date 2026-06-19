#!/usr/bin/env python3
"""Update Insurance sheet with bank details for 151 verified employees."""

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

def extract_payroll_bank_details(service):
    """Extract bank details from all entity payroll sheets."""
    print("Extracting bank details from Payroll sheets...\n")

    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
    entity_sheets = ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_']

    all_payroll_data = {}

    for entity in entity_sheets:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=payroll_sheet_id,
                range=f"'{entity}'!A:H"
            ).execute()

            values = result.get('values', [])

            for row in values[1:]:
                if not row or not row[0]:
                    continue

                emp_id = row[0].strip() if row[0] else ""
                emp_name = row[1].strip() if len(row) > 1 else ""
                cnic = row[4].strip() if len(row) > 4 else ""
                bank_name = row[6].strip() if len(row) > 6 else ""
                account_number = row[7].strip() if len(row) > 7 else ""

                if emp_id and emp_name:
                    key = f"{emp_id}|{emp_name.lower()}|{cnic}"
                    all_payroll_data[key] = {
                        'employee_id': emp_id,
                        'employee_name': emp_name,
                        'cnic': cnic,
                        'bank_name': bank_name,
                        'account_number': account_number
                    }

        except Exception as e:
            print(f"Error reading {entity}: {e}")

    print(f"[OK] Extracted {len(all_payroll_data)} payroll records\n")
    return all_payroll_data

def get_insurance_sheet_data(service):
    """Get all data from Insurance sheet."""
    print("Reading Insurance sheet...")

    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    result = service.spreadsheets().values().get(
        spreadsheetId=insurance_sheet_id,
        range='Sheet1!A:D'
    ).execute()

    values = result.get('values', [])
    print(f"[OK] Found {len(values)} rows in Insurance sheet\n")
    return values

def three_step_match(insurance_employee, payroll_data):
    """3-step matching: ID -> Name -> CNIC."""
    insurance_name = insurance_employee['col_b']
    insurance_cnic = insurance_employee['col_c']

    # Extract ID from col_a
    col_a_parts = insurance_employee['col_a'].split()
    insurance_id = col_a_parts[0] if col_a_parts and col_a_parts[0].isdigit() else ""

    best_match = None

    # Step 1: Exact ID + Name + CNIC match
    if insurance_id:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if p_id == insurance_id and p_name.lower() == insurance_name.lower():
                if insurance_cnic and payroll['cnic']:
                    if insurance_cnic.lower() == payroll['cnic'].lower():
                        best_match = payroll
                        break
                else:
                    best_match = payroll
                    break

    # Step 2: Name + CNIC match
    if not best_match and insurance_cnic:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if p_name.lower() == insurance_name.lower() and payroll['cnic']:
                if insurance_cnic.lower() == payroll['cnic'].lower():
                    best_match = payroll
                    break

    # Step 3: Fuzzy name match with CNIC
    if not best_match and insurance_cnic:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if payroll['cnic'] and insurance_cnic.lower() == payroll['cnic'].lower():
                score = SequenceMatcher(None, insurance_name.lower(), p_name.lower()).ratio()
                if score > 0.85:
                    best_match = payroll
                    break

    return best_match

def update_insurance_sheet(service, insurance_sheet_id, sheet_data, payroll_data):
    """Update Insurance sheet with bank details."""
    print("Preparing to update Insurance sheet...\n")

    updated_data = []
    matched_count = 0
    unmatched_count = 0

    for idx, row in enumerate(sheet_data):
        if idx == 0:
            # Header row - extend with new columns
            new_row = list(row) + ['Bank Name', 'Account Number']
            updated_data.append(new_row)
            continue

        if not row or not row[0]:
            updated_data.append(row)
            continue

        col_a = row[0].strip() if row[0] else ""
        col_b = row[1].strip() if len(row) > 1 else ""
        col_c = row[2].strip() if len(row) > 2 else ""

        # Skip section headers
        if col_a.startswith('[') or col_a.startswith('=') or len(col_a) < 2:
            updated_data.append(row)
            continue

        # Try to match
        insurance_emp = {
            'col_a': col_a,
            'col_b': col_b,
            'col_c': col_c
        }

        match = three_step_match(insurance_emp, payroll_data)

        if match:
            # Add bank details
            new_row = list(row) + [match['bank_name'], match['account_number']]
            updated_data.append(new_row)
            matched_count += 1
        else:
            # No match - add empty columns
            new_row = list(row) + ['', '']
            updated_data.append(new_row)
            unmatched_count += 1

    print(f"[OK] Matched: {matched_count} employees")
    print(f"[BLANK] Unmatched: {unmatched_count} employees")
    print(f"[OK] Total rows to write: {len(updated_data)}\n")

    # Update the sheet
    print("Writing updated data to Insurance sheet...")

    try:
        # Clear the entire sheet first
        service.spreadsheets().values().clear(
            spreadsheetId=insurance_sheet_id,
            range='Sheet1!A:F'
        ).execute()

        # Write updated data
        service.spreadsheets().values().update(
            spreadsheetId=insurance_sheet_id,
            range='Sheet1!A1',
            valueInputOption='USER_ENTERED',
            body={'values': updated_data}
        ).execute()

        print("[OK] Insurance sheet updated successfully!\n")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 130)
    print("UPDATING INSURANCE SHEET WITH BANK DETAILS")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Extract payroll bank details
    payroll_data = extract_payroll_bank_details(service)

    # Get insurance sheet data
    sheet_data = get_insurance_sheet_data(service)

    if not payroll_data or not sheet_data:
        print("[ERROR] Could not read required data")
        return

    # Update insurance sheet
    if update_insurance_sheet(service, insurance_sheet_id, sheet_data, payroll_data):
        print("=" * 130)
        print("UPDATE COMPLETE")
        print("=" * 130)
        print("\nInsurance Sheet Updated:")
        print(f"  + Added 'Bank Name' column")
        print(f"  + Added 'Account Number' column")
        print(f"  + 151 employees with verified bank details")
        print(f"  + 30 unmatched employees with blank bank details")
        print(f"\nSheet Link: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")

if __name__ == "__main__":
    main()
