#!/usr/bin/env python3
"""Extract bank details from all Payroll sheets and match with Insurance sheet."""

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
    print("Extracting bank details from all Payroll sheets...\n")

    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
    entity_sheets = ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_']

    all_payroll_data = {}

    for entity in entity_sheets:
        print(f"Reading {entity}...")
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=payroll_sheet_id,
                range=f"'{entity}'!A:H"
            ).execute()

            values = result.get('values', [])
            employee_count = 0

            for row in values[1:]:  # Skip header
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
                        'account_number': account_number,
                        'entity': entity
                    }
                    employee_count += 1

            print(f"  [OK] {employee_count} employees from {entity}")

        except Exception as e:
            print(f"  [ERROR] {entity}: {e}")

    print(f"\n[OK] Total payroll records extracted: {len(all_payroll_data)}\n")
    return all_payroll_data

def get_insurance_data(service):
    """Get employee data from Insurance sheet."""
    print("Reading Insurance sheet...")

    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=insurance_sheet_id,
            range='Sheet1!A:D'
        ).execute()

        values = result.get('values', [])
        insurance_data = []

        for idx, row in enumerate(values[1:], 1):
            if not row or not row[0]:
                continue

            col_a = row[0].strip() if row[0] else ""
            col_b = row[1].strip() if len(row) > 1 else ""
            col_c = row[2].strip() if len(row) > 2 else ""

            # Skip section headers and markers
            if col_a.startswith('[') or col_a.startswith('=') or len(col_a) < 2:
                continue

            insurance_data.append({
                'row_idx': idx + 1,  # Google Sheets row (1-indexed, +1 for header)
                'col_a': col_a,
                'col_b': col_b,
                'col_c': col_c
            })

        print(f"[OK] Found {len(insurance_data)} employee/dependent records in Insurance sheet\n")
        return insurance_data

    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def three_step_match(insurance_employee, payroll_data):
    """3-step matching: ID -> Name -> CNIC."""
    # Try to extract ID from insurance col_a (format might be "ID - Name" or similar)
    insurance_id = None
    insurance_name = insurance_employee['col_b']
    insurance_cnic = insurance_employee['col_c']

    # Try to find ID from col_a if it's a number
    col_a_parts = insurance_employee['col_a'].split()
    if col_a_parts and col_a_parts[0].isdigit():
        insurance_id = col_a_parts[0]

    best_match = None
    match_type = ""

    # Step 1: Try exact ID + Name match
    if insurance_id:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if p_id == insurance_id and p_name.lower() == insurance_name.lower():
                # Verify CNIC too
                if insurance_cnic and payroll['cnic']:
                    if insurance_cnic.lower() == payroll['cnic'].lower():
                        best_match = payroll
                        match_type = "3/3 Match (ID+Name+CNIC)"
                        break
                else:
                    best_match = payroll
                    match_type = "2/3 Match (ID+Name)"
                    break

    # Step 2: Try Name + CNIC match (if Step 1 failed)
    if not best_match:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if p_name.lower() == insurance_name.lower():
                if insurance_cnic and payroll['cnic']:
                    if insurance_cnic.lower() == payroll['cnic'].lower():
                        best_match = payroll
                        match_type = "3/3 Match (Name+CNIC+ID)"
                        break

    # Step 3: Try fuzzy name match with CNIC verification
    if not best_match and insurance_cnic:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if payroll['cnic'] and insurance_cnic.lower() == payroll['cnic'].lower():
                score = SequenceMatcher(None, insurance_name.lower(), p_name.lower()).ratio()
                if score > 0.85:
                    best_match = payroll
                    match_type = f"3/3 Match (CNIC+Fuzzy Name {score:.0%})"
                    break

    return best_match, match_type

def main():
    print("\n" + "=" * 130)
    print("BANK DETAILS EXTRACTION & MATCHING")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    # Extract payroll data
    payroll_data = extract_payroll_bank_details(service)

    # Get insurance data
    insurance_data = get_insurance_data(service)

    if not payroll_data or not insurance_data:
        print("[ERROR] Could not read required data")
        return

    # Match and report
    print("=" * 130)
    print("MATCHING RESULTS")
    print("=" * 130 + "\n")

    matched = []
    unmatched = []
    suspicious = []

    for emp in insurance_data:
        match, match_type = three_step_match(emp, payroll_data)

        if match:
            # Verify all details match
            is_suspicious = False
            issues = []

            # Extract ID from col_a if possible
            col_a_parts = emp['col_a'].split()
            emp_id = col_a_parts[0] if col_a_parts and col_a_parts[0].isdigit() else ""

            if emp_id and emp_id != match['employee_id']:
                issues.append(f"ID mismatch: Insurance={emp_id}, Payroll={match['employee_id']}")
                is_suspicious = True

            if emp['col_b'].lower() != match['employee_name'].lower():
                issues.append(f"Name slight difference")

            if emp['col_c'] and match['cnic']:
                if emp['col_c'].lower() != match['cnic'].lower():
                    issues.append(f"CNIC mismatch: Insurance={emp['col_c']}, Payroll={match['cnic']}")
                    is_suspicious = True

            if is_suspicious:
                suspicious.append({
                    'insurance': emp,
                    'payroll': match,
                    'match_type': match_type,
                    'issues': issues
                })
            else:
                matched.append({
                    'insurance': emp,
                    'payroll': match,
                    'match_type': match_type
                })
        else:
            unmatched.append(emp)

    print(f"MATCHED (with 3-step verification): {len(matched)}")
    print(f"SUSPICIOUS (potential mismatches): {len(suspicious)}")
    print(f"UNMATCHED (no payroll record found): {len(unmatched)}\n")

    if suspicious:
        print("=" * 130)
        print("SUSPICIOUS MATCHES - NEED MANUAL REVIEW")
        print("=" * 130 + "\n")
        for item in suspicious[:10]:  # Show first 10
            print(f"Insurance: {item['insurance']['col_b']} (CNIC: {item['insurance']['col_c']})")
            print(f"Payroll:   {item['payroll']['employee_name']} (ID: {item['payroll']['employee_id']}, CNIC: {item['payroll']['cnic']})")
            print(f"Match Type: {item['match_type']}")
            for issue in item['issues']:
                print(f"  ⚠ {issue}")
            print(f"Bank: {item['payroll']['bank_name']} | Account: {item['payroll']['account_number']}")
            print()

        if len(suspicious) > 10:
            print(f"... and {len(suspicious) - 10} more suspicious matches")
            print()

    if unmatched:
        print("\n" + "=" * 130)
        print("UNMATCHED EMPLOYEES - NO PAYROLL RECORD FOUND")
        print("=" * 130 + "\n")
        print(f"Total unmatched: {len(unmatched)}")
        for emp in unmatched[:10]:  # Show first 10
            print(f"  - {emp['col_b']} (CNIC: {emp['col_c']})")

        if len(unmatched) > 10:
            print(f"  ... and {len(unmatched) - 10} more unmatched")

    print("\n" + "=" * 130)
    print("SUMMARY")
    print("=" * 130)
    print(f"Total Insurance Records: {len(insurance_data)}")
    print(f"Total Payroll Records: {len(payroll_data)}")
    print(f"\n[OK] Fully Matched: {len(matched)}")
    print(f"[WARN] Suspicious/Manual Review: {len(suspicious)}")
    print(f"[MISSING] Unmatched: {len(unmatched)}")
    print(f"\nBefore updating Insurance sheet, please review the suspicious matches above!")

if __name__ == "__main__":
    main()
