#!/usr/bin/env python3
"""Complete cross-check: Payroll + Addition/Deletion vs Insurance."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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

def get_all_deletions_2026(service):
    """Get all employee deletions from Jan 2026 onwards."""
    print("Reading Addition/Deletion sheet for 2026 deletions...\n")

    add_del_sheet_id = '18x6R4Gl3P_D-Dn_HHtLpXbpwQnqVafO6rekvovcVICk'
    months_2026 = ['January 2026', 'February 2026', 'March 2026', 'April 2026', 'May 2026', 'June 2026']

    all_deletions = set()
    all_additions = set()

    for month in months_2026:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=add_del_sheet_id,
                range=f"'{month}'!A:B"
            ).execute()

            values = result.get('values', [])
            in_deletion = False
            in_addition = False

            for row in values:
                if not row:
                    continue

                cell_value = row[0].strip() if row[0] else ""

                # Check for section headers
                if 'Employee Deletion' in cell_value:
                    in_deletion = True
                    in_addition = False
                    continue
                elif 'Employee Addition' in cell_value:
                    in_deletion = False
                    in_addition = True
                    continue
                elif cell_value.lower() in ['name', 'designation', 'entity/branch (payroll)', 'email']:
                    continue
                elif cell_value in ['', 'No']:
                    continue

                # Collect data
                if in_deletion and cell_value:
                    all_deletions.add(cell_value.lower())
                elif in_addition and cell_value:
                    all_additions.add(cell_value.lower())

        except Exception as e:
            print(f"Error reading {month}: {e}")

    print(f"[OK] Total deletions (2026): {len(all_deletions)}")
    print(f"[OK] Total additions (2026): {len(all_additions)}\n")

    return all_deletions, all_additions

def main():
    print("\n" + "=" * 130)
    print("COMPREHENSIVE INSURANCE CROSS-CHECK")
    print("Payroll + Addition/Deletion Data vs Insurance Sheet")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    # Get deletions and additions from 2026
    deletions_2026, additions_2026 = get_all_deletions_2026(service)

    # Get payroll employees
    print("Reading Payroll employees...\n")
    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
    entity_sheets = ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_']

    payroll_employees = {}
    for entity in entity_sheets:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=payroll_sheet_id,
                range=f"'{entity}'!A:B"
            ).execute()

            values = result.get('values', [])
            for row in values[1:]:
                if row and len(row) > 1:
                    emp_id = row[0].strip() if row[0] else ""
                    emp_name = row[1].strip() if row[1] else ""
                    if emp_id and emp_name:
                        payroll_employees[emp_name.lower()] = emp_name
        except:
            pass

    print(f"[OK] Total payroll employees: {len(payroll_employees)}\n")

    # Get insurance employees
    print("Reading Insurance sheet...\n")
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    result = service.spreadsheets().values().get(
        spreadsheetId=insurance_sheet_id,
        range='Sheet1!A:B'
    ).execute()

    values = result.get('values', [])
    insurance_employees = {}
    for row in values[1:]:
        if row and len(row) > 1:
            emp_id = row[0].strip() if row[0] else ""
            emp_name = row[1].strip() if row[1] else ""
            if emp_id and emp_id.isdigit() and emp_name:
                insurance_employees[emp_name.lower()] = emp_name

    print(f"[OK] Total insurance employees: {len(insurance_employees)}\n")

    # Analysis
    print("=" * 130)
    print("ANALYSIS")
    print("=" * 130 + "\n")

    # Employees to REMOVE (in Insurance but marked as deleted)
    should_remove = []
    for emp_lower in insurance_employees.keys():
        if emp_lower in deletions_2026:
            should_remove.append(insurance_employees[emp_lower])

    # Employees to ADD (in Payroll but not in Insurance + in additions list)
    should_add = []
    for emp_lower, emp_name in payroll_employees.items():
        if emp_lower not in insurance_employees:
            if emp_lower in additions_2026 or emp_lower not in deletions_2026:
                should_add.append(emp_name)

    # Invalid entries (in Insurance but not in Payroll and not in additions)
    invalid = []
    for emp_lower, emp_name in insurance_employees.items():
        if emp_lower not in payroll_employees and emp_lower not in additions_2026:
            invalid.append(emp_name)

    print(f"🔴 SHOULD REMOVE (in Insurance + marked deleted in 2026): {len(should_remove)}")
    if should_remove:
        for emp in sorted(should_remove)[:20]:
            print(f"  - {emp}")
        if len(should_remove) > 20:
            print(f"  ... and {len(should_remove) - 20} more")

    print(f"\n🟢 SHOULD ADD (in Payroll + not in Insurance): {len(should_add)}")
    if should_add:
        for emp in sorted(should_add)[:20]:
            print(f"  + {emp}")
        if len(should_add) > 20:
            print(f"  ... and {len(should_add) - 20} more")

    print(f"\n⚠️  VERIFY (in Insurance but not in Payroll + not in additions): {len(invalid)}")
    if invalid:
        for emp in sorted(invalid)[:20]:
            print(f"  ? {emp}")
        if len(invalid) > 20:
            print(f"  ... and {len(invalid) - 20} more")

    print("\n" + "=" * 130)
    print("SUMMARY")
    print("=" * 130)
    print(f"Payroll Employees: {len(payroll_employees)}")
    print(f"Insurance Employees: {len(insurance_employees)}")
    print(f"2026 Deletions: {len(deletions_2026)}")
    print(f"2026 Additions: {len(additions_2026)}")
    print(f"\nActions Needed:")
    print(f"  - Remove {len(should_remove)} employees")
    print(f"  - Add {len(should_add)} employees")
    print(f"  - Verify {len(invalid)} employees")

if __name__ == "__main__":
    main()
