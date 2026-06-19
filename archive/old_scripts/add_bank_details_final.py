#!/usr/bin/env python3
"""Add bank details using 3-column verification: Employee ID + Name + CNIC"""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_google_credentials():
    token_path = 'c:/Agent Oreo/token.json'
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def get_payroll_bank_mapping(service):
    """Build Employee ID + Name + CNIC → Bank Name + Account mapping from Payroll."""
    print("Reading March 2026 Payroll (all entities)...\n")

    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
    entity_sheets = ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_']

    bank_mapping = {}  # Key: (emp_id, emp_name_lower, cnic_lower) → {bank_name, account_number}

    for entity in entity_sheets:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=payroll_sheet_id,
                range=f"'{entity}'!A:H"
            ).execute()

            values = result.get('values', [])

            for row in values[1:]:
                if not row or len(row) < 8:
                    continue

                emp_id = row[0].strip() if row[0] else ""
                emp_name = row[1].strip() if row[1] else ""
                cnic = row[4].strip() if len(row) > 4 else ""
                bank_name = row[6].strip() if len(row) > 6 else ""
                account_number = row[7].strip() if len(row) > 7 else ""

                if emp_id and emp_name and cnic:
                    key = (emp_id, emp_name.lower(), cnic.lower())
                    bank_mapping[key] = {
                        'bank_name': bank_name,
                        'account_number': account_number
                    }

            print(f"  {entity:<30} processed")

        except Exception as e:
            print(f"  {entity:<30} [ERROR: {e}]")

    print(f"\n[OK] Built mapping with {len(bank_mapping)} payroll records\n")
    return bank_mapping

def get_insurance_data(service):
    """Read Insurance sheet and get all employee data."""
    print("Reading Insurance sheet...\n")

    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    result = service.spreadsheets().values().get(
        spreadsheetId=insurance_sheet_id,
        range='Sheet1!A:L'
    ).execute()

    values = result.get('values', [])
    print(f"[OK] Found {len(values)} rows in Insurance sheet\n")

    return values

def match_and_update(insurance_data, bank_mapping, service):
    """Match employees and prepare bank detail updates."""
    print("Matching employees using 3-column verification...\n")
    print(f"{'Col':<5} {'Employee Name':<40} {'Match Result':<30} {'Bank':<20}")
    print("-" * 130)

    matched_count = 0
    updates = []
    no_match = []

    for row_idx, row in enumerate(insurance_data[1:], 2):  # Start from row 2 (after header)
        if not row or len(row) < 3:
            continue

        emp_id = row[0].strip() if row[0] else ""
        emp_name = row[1].strip() if len(row) > 1 and row[1] else ""
        cnic = row[2].strip() if len(row) > 2 and row[2] else ""

        # Skip section headers
        if emp_id.startswith('[') or emp_id.startswith('=') or not emp_id:
            continue

        # Try to find match in payroll
        key = (emp_id, emp_name.lower(), cnic.lower())

        if key in bank_mapping:
            bank_data = bank_mapping[key]
            
            # Prepare update for columns K and L
            updates.append({
                'range': f'Sheet1!K{row_idx}',
                'values': [[bank_data['bank_name']]]
            })
            updates.append({
                'range': f'Sheet1!L{row_idx}',
                'values': [[bank_data['account_number']]]
            })

            matched_count += 1
            try:
                print(f"{row_idx:<5} {emp_name[:40]:<40} MATCHED {bank_data['bank_name'][:20]:<30}")
            except:
                print(f"{row_idx:<5} [Non-ASCII name]            MATCHED")

        else:
            no_match.append({
                'row': row_idx,
                'emp_id': emp_id,
                'emp_name': emp_name,
                'cnic': cnic
            })

    print(f"\n[OK] Matched: {matched_count}")
    print(f"[BLANK] No match: {len(no_match)}\n")

    return updates, matched_count, no_match

def apply_updates(service, updates):
    """Apply bank detail updates to Insurance sheet."""
    if not updates:
        print("[WARNING] No updates to apply")
        return False

    print(f"Applying {len(updates)} updates to Insurance sheet...\n")

    try:
        insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=insurance_sheet_id,
            body={'data': updates, 'valueInputOption': 'USER_ENTERED'}
        ).execute()

        print("[OK] Bank details added successfully!\n")
        return True

    except Exception as e:
        print(f"[ERROR] {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 130)
    print("ADD BANK DETAILS TO INSURANCE SHEET")
    print("3-Column Verification: Employee ID + Employee Name + CNIC")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    service = build('sheets', 'v4', credentials=creds)

    # Get payroll bank mapping
    bank_mapping = get_payroll_bank_mapping(service)

    # Get insurance data
    insurance_data = get_insurance_data(service)

    # Match and prepare updates
    updates, matched_count, no_match = match_and_update(insurance_data, bank_mapping, service)

    # Apply updates
    if apply_updates(service, updates):
        print("=" * 130)
        print("SUMMARY")
        print("=" * 130)
        print(f"\nBank Details Added:")
        print(f"  Column K (Bank Name): {matched_count} employees")
        print(f"  Column L (Account Number): {matched_count} employees")
        print(f"  No match (left blank): {len(no_match)} employees")
        print(f"\nInsurance Sheet: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")

if __name__ == "__main__":
    main()
