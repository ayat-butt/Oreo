#!/usr/bin/env python3
"""Populate existing Bank Name (Col I) and Account # (Col J) columns with verified payroll data."""

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

def three_step_match(insurance_name, insurance_cnic, payroll_data):
    """3-step matching: ID -> Name -> CNIC."""
    best_match = None

    # Step 1: Exact name match
    for key, payroll in payroll_data.items():
        p_id, p_name, p_cnic = key.split('|')
        if p_name.lower() == insurance_name.lower():
            # Verify CNIC if available
            if insurance_cnic and payroll['cnic']:
                if insurance_cnic.lower() == payroll['cnic'].lower():
                    best_match = payroll
                    break
            else:
                best_match = payroll
                break

    # Step 2: CNIC match (if name match failed)
    if not best_match and insurance_cnic:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if payroll['cnic'] and insurance_cnic.lower() == payroll['cnic'].lower():
                best_match = payroll
                break

    # Step 3: Fuzzy name match
    if not best_match:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            score = SequenceMatcher(None, insurance_name.lower(), p_name.lower()).ratio()
            if score > 0.85:
                if insurance_cnic and payroll['cnic']:
                    if insurance_cnic.lower() == payroll['cnic'].lower():
                        best_match = payroll
                        break
                else:
                    best_match = payroll
                    break

    return best_match

def main():
    print("\n" + "=" * 130)
    print("POPULATING EXISTING BANK COLUMNS (I & J)")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Extract payroll bank details
    payroll_data = extract_payroll_bank_details(service)

    # Get insurance sheet data
    print("Reading Insurance sheet...")
    result = service.spreadsheets().values().get(
        spreadsheetId=insurance_sheet_id,
        range='Sheet1!A:K'
    ).execute()

    values = result.get('values', [])
    print(f"[OK] Found {len(values)} rows\n")

    # Prepare updates
    print("Matching and preparing updates...\n")

    updates = []
    matched_count = 0
    unmatched_count = 0

    for row_idx, row in enumerate(values[1:], 2):  # Start from row 2
        if not row or not row[1]:  # Skip if no employee name
            continue

        emp_name = row[1].strip() if len(row) > 1 else ""
        emp_cnic = row[2].strip() if len(row) > 2 else ""  # Assuming CNIC is in column C

        # Skip section headers
        if emp_name.startswith('[') or emp_name.startswith('=') or len(emp_name) < 2:
            continue

        # Match with payroll
        match = three_step_match(emp_name, emp_cnic, payroll_data)

        if match:
            # Update columns I (Bank Name) and J (Account #)
            updates.append({
                'range': f'Sheet1!I{row_idx}',
                'values': [[match['bank_name']]]
            })
            updates.append({
                'range': f'Sheet1!J{row_idx}',
                'values': [[match['account_number']]]
            })
            matched_count += 1
        else:
            unmatched_count += 1

    print(f"Matched: {matched_count} employees")
    print(f"Unmatched: {unmatched_count} employees")
    print(f"Total updates to apply: {len(updates)}\n")

    if updates:
        print("Applying updates to Insurance sheet...\n")

        try:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=insurance_sheet_id,
                body={'data': updates, 'valueInputOption': 'USER_ENTERED'}
            ).execute()

            print("[OK] Bank details populated successfully!\n")

            print("=" * 130)
            print("UPDATE COMPLETE")
            print("=" * 130)
            print(f"\nColumn I (Bank Name): {matched_count} employees populated")
            print(f"Column J (Account #): {matched_count} employees populated")
            print(f"Unmatched (blank): {unmatched_count} employees")
            print(f"\nSheet: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[WARNING] No updates to apply")

if __name__ == "__main__":
    main()
