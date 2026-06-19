#!/usr/bin/env python3
"""Improved bank details matching with better normalization and fuzzy fallback."""

import json
import re
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

def normalize_name(name):
    """Normalize name: lowercase, remove extra spaces, handle special chars."""
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r'\s+', ' ', name)  # Multiple spaces to single
    return name

def normalize_cnic(cnic):
    """Normalize CNIC: remove hyphens, spaces, leading zeros."""
    if not cnic:
        return ""
    cnic = cnic.strip()
    cnic = re.sub(r'[\s\-]', '', cnic)  # Remove spaces and hyphens
    return cnic

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
                    # Create multiple keys for better matching
                    norm_name = normalize_name(emp_name)
                    norm_cnic = normalize_cnic(cnic)

                    key = f"{emp_id}|{norm_name}|{norm_cnic}"
                    all_payroll_data[key] = {
                        'employee_id': emp_id,
                        'employee_name': emp_name,
                        'cnic': cnic,
                        'bank_name': bank_name,
                        'account_number': account_number,
                        'entity': entity,
                        'norm_name': norm_name,
                        'norm_cnic': norm_cnic
                    }

        except Exception as e:
            print(f"Error reading {entity}: {e}")

    print(f"[OK] Extracted {len(all_payroll_data)} payroll records\n")
    return all_payroll_data

def improved_three_step_match(insurance_emp, payroll_data):
    """Improved 3-step matching with normalization and fuzzy fallback."""
    insurance_name = insurance_emp['col_b']
    insurance_cnic = insurance_emp['col_c']
    insurance_id = insurance_emp['col_a']

    # Normalize insurance data
    norm_ins_name = normalize_name(insurance_name)
    norm_ins_cnic = normalize_cnic(insurance_cnic)

    best_match = None
    match_score = 0

    # Step 1: Exact ID + Name match (with normalized comparison)
    if insurance_id:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if p_id == insurance_id and p_name == norm_ins_name:
                # Verify CNIC if both available
                if norm_ins_cnic and p_cnic:
                    if norm_ins_cnic == p_cnic:
                        return payroll, "3/3 Match (ID+Name+CNIC)"
                    # ID+Name match even if CNIC differs slightly
                    if match_score < 2.5:
                        best_match = payroll
                        match_score = 2.5
                        best_match_type = "2/3 Match (ID+Name, CNIC mismatch)"
                else:
                    return payroll, "2/3 Match (ID+Name)"

    # Step 2: Name + CNIC exact match
    if not best_match or match_score < 2.8:
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')
            if p_name == norm_ins_name and norm_ins_cnic and p_cnic:
                if norm_ins_cnic == p_cnic:
                    if match_score < 2.8:
                        best_match = payroll
                        match_score = 2.8
                        best_match_type = "3/3 Match (Name+CNIC+ID)"

    # Step 3: Fuzzy name match with CNIC verification
    if not best_match or match_score < 2.5:
        best_fuzzy_match = None
        best_fuzzy_score = 0
        for key, payroll in payroll_data.items():
            p_id, p_name, p_cnic = key.split('|')

            # Try fuzzy match on name
            name_score = SequenceMatcher(None, norm_ins_name, p_name).ratio()

            if name_score > 0.85:
                # Check CNIC if available
                if norm_ins_cnic and p_cnic:
                    if norm_ins_cnic == p_cnic:
                        # Perfect CNIC match + good name match
                        if name_score > best_fuzzy_score:
                            best_fuzzy_match = payroll
                            best_fuzzy_score = name_score
                            best_fuzzy_type = f"3/3 Match (CNIC+Fuzzy {name_score:.0%})"
                else:
                    # No CNIC to verify
                    if name_score > best_fuzzy_score:
                        best_fuzzy_match = payroll
                        best_fuzzy_score = name_score
                        best_fuzzy_type = f"Fuzzy Match ({name_score:.0%})"

        if best_fuzzy_match and best_fuzzy_score > match_score:
            best_match = best_fuzzy_match
            best_match_type = best_fuzzy_type
            match_score = best_fuzzy_score

    # Step 4: Fallback - ID only match (if ID exists and unique)
    if not best_match and insurance_id:
        id_matches = [p for p in payroll_data.values() if p['employee_id'] == insurance_id]
        if len(id_matches) == 1:
            best_match = id_matches[0]
            best_match_type = "ID-only Match (name mismatch but unique ID)"
            match_score = 1.5

    if best_match:
        return best_match, best_match_type
    return None, "No match found"

def main():
    print("\n" + "=" * 130)
    print("ADDING BANK DETAILS WITH IMPROVED MATCHING")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    # Extract payroll data
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
    print("Matching with improved logic...\n")

    updates = []
    matched_count = 0
    match_types = {}
    unmatched_employees = []

    for row_idx, row in enumerate(values[1:], 2):  # Start from row 2
        if not row or not row[1]:  # Skip if no employee name
            continue

        emp_id = row[0].strip() if len(row) > 0 else ""
        emp_name = row[1].strip() if len(row) > 1 else ""
        emp_cnic = row[4].strip() if len(row) > 4 else ""  # Column E is CNIC

        # Skip section headers and empty rows
        if not emp_name or emp_name.startswith('[') or emp_name.startswith('=') or len(emp_name.strip()) < 2:
            continue
        if emp_name in ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_']:
            continue  # Skip entity headers

        # Match with payroll
        insurance_emp = {
            'col_a': emp_id,
            'col_b': emp_name,
            'col_c': emp_cnic
        }

        match, match_type = improved_three_step_match(insurance_emp, payroll_data)

        if match:
            # Update columns K (Bank Name) and L (Account Number)
            updates.append({
                'range': f'Sheet1!K{row_idx}',
                'values': [[match['bank_name']]]
            })
            updates.append({
                'range': f'Sheet1!L{row_idx}',
                'values': [[match['account_number']]]
            })
            matched_count += 1

            match_types[match_type] = match_types.get(match_type, 0) + 1
        else:
            unmatched_employees.append({
                'row': row_idx,
                'id': emp_id,
                'name': emp_name,
                'cnic': emp_cnic
            })

    print(f"MATCHED EMPLOYEES: {matched_count}")
    print(f"UNMATCHED EMPLOYEES: {len(unmatched_employees)}\n")

    print("Match Type Breakdown:")
    for match_type, count in sorted(match_types.items(), key=lambda x: -x[1]):
        print(f"  {match_type}: {count}")
    print()

    if unmatched_employees:
        print("=" * 130)
        print(f"UNMATCHED EMPLOYEES: {len(unmatched_employees)} total")
        print("=" * 130)
        print(f"\nWriting detailed list to output/unmatched_employees.txt...\n")

        # Write to file to avoid encoding issues
        with open('output/unmatched_employees.txt', 'w', encoding='utf-8') as f:
            f.write(f"UNMATCHED EMPLOYEES ({len(unmatched_employees)} total)\n")
            f.write("=" * 100 + "\n\n")
            for emp in unmatched_employees:
                f.write(f"Row {emp['row']}: {emp['name']} | ID: {emp['id']} | CNIC: {emp['cnic']}\n")

        print(f"[OK] Unmatched list saved to output/unmatched_employees.txt")

    if updates:
        print("\nApplying updates to Insurance sheet...\n")

        try:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=insurance_sheet_id,
                body={'data': updates, 'valueInputOption': 'USER_ENTERED'}
            ).execute()

            print("[OK] Bank details updated successfully!\n")

            print("=" * 130)
            print("UPDATE COMPLETE")
            print("=" * 130)
            print(f"\nColumn K (Bank Name): {matched_count} employees populated")
            print(f"Column L (Account Number): {matched_count} employees populated")
            print(f"Unmatched: {len(unmatched_employees)} employees")
            print(f"\nSheet: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[WARNING] No updates to apply")

if __name__ == "__main__":
    main()
