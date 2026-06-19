#!/usr/bin/env python3
"""Cross-check March 2026 Payroll vs Insurance sheet."""

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

def get_payroll_employees(service):
    """Get all unique employees from all payroll sheets."""
    print("Reading March 2026 Payroll (all entities)...\n")

    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
    entity_sheets = ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_']

    all_payroll_employees = {}
    entity_breakdown = {}

    for entity in entity_sheets:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=payroll_sheet_id,
                range=f"'{entity}'!A:E"
            ).execute()

            values = result.get('values', [])
            entity_count = 0

            for row in values[1:]:
                if not row or not row[0]:
                    continue

                emp_id = row[0].strip() if row[0] else ""
                emp_name = row[1].strip() if len(row) > 1 else ""
                cnic = row[4].strip() if len(row) > 4 else ""

                if emp_id and emp_name:
                    key = emp_name.lower()
                    all_payroll_employees[key] = {
                        'name': emp_name,
                        'id': emp_id,
                        'cnic': cnic,
                        'entity': entity
                    }
                    entity_count += 1

            entity_breakdown[entity] = entity_count
            print(f"  {entity:<30} {entity_count:>3} employees")

        except Exception as e:
            print(f"  {entity:<30} [ERROR: {e}]")

    print(f"\n[OK] Total unique payroll employees: {len(all_payroll_employees)}\n")
    return all_payroll_employees, entity_breakdown

def get_insurance_employees(service):
    """Get all unique employees from Insurance sheet."""
    print("Reading Insurance sheet...\n")

    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    result = service.spreadsheets().values().get(
        spreadsheetId=insurance_sheet_id,
        range='Sheet1!A:D'
    ).execute()

    values = result.get('values', [])
    insurance_employees = {}
    employee_count = 0
    dependent_count = 0

    for row in values[1:]:
        if not row or not row[1]:
            continue

        emp_id = row[0].strip() if row[0] else ""
        emp_name = row[1].strip() if len(row) > 1 else ""

        # Skip section headers
        if emp_name.startswith('[') or emp_name.startswith('=') or len(emp_name) < 2:
            continue

        # Check if it's an employee or dependent (employees have ID)
        if emp_id and emp_id.isdigit():
            key = emp_name.lower()
            insurance_employees[key] = {
                'name': emp_name,
                'id': emp_id
            }
            employee_count += 1
        else:
            # It's likely a dependent
            dependent_count += 1

    print(f"[OK] Total insurance employees: {employee_count}")
    print(f"[OK] Total insurance dependents: {dependent_count}\n")

    return insurance_employees, employee_count, dependent_count

def main():
    print("\n" + "=" * 130)
    print("CROSS-CHECK: MARCH 2026 PAYROLL vs INSURANCE SHEET")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    # Get payroll data
    payroll_employees, entity_breakdown = get_payroll_employees(service)

    # Get insurance data
    insurance_employees, insurance_emp_count, insurance_dep_count = get_insurance_employees(service)

    print("=" * 130)
    print("COMPARISON")
    print("=" * 130 + "\n")

    # Find missing in insurance
    missing_in_insurance = []
    for name, payroll in payroll_employees.items():
        if name not in insurance_employees:
            missing_in_insurance.append(payroll)

    # Find missing in payroll
    missing_in_payroll = []
    for name, insurance in insurance_employees.items():
        if name not in payroll_employees:
            missing_in_payroll.append(insurance)

    print(f"Payroll Employees: {len(payroll_employees)}")
    print(f"Insurance Employees: {insurance_emp_count}")
    print(f"Insurance Dependents: {insurance_dep_count}\n")

    print(f"MISSING IN INSURANCE: {len(missing_in_insurance)} employees")
    print(f"MISSING IN PAYROLL: {len(missing_in_payroll)} employees\n")

    if missing_in_insurance:
        print("=" * 130)
        print(f"EMPLOYEES IN PAYROLL BUT NOT IN INSURANCE ({len(missing_in_insurance)})")
        print("=" * 130 + "\n")
        
        print(f"{'Entity':<30} {'Employee ID':<15} {'Employee Name':<40} {'CNIC':<20}")
        print("-" * 130)
        
        for emp in sorted(missing_in_insurance, key=lambda x: (x['entity'], x['name']))[:50]:
            try:
                print(f"{emp['entity']:<30} {emp['id']:<15} {emp['name']:<40} {emp['cnic']:<20}")
            except:
                print(f"{emp['entity']:<30} {emp['id']:<15} [Non-ASCII name]")

        if len(missing_in_insurance) > 50:
            print(f"\n... and {len(missing_in_insurance) - 50} more")

    if missing_in_payroll:
        print("\n" + "=" * 130)
        print(f"EMPLOYEES IN INSURANCE BUT NOT IN PAYROLL ({len(missing_in_payroll)})")
        print("=" * 130 + "\n")
        
        print(f"{'Employee ID':<15} {'Employee Name':<40}")
        print("-" * 130)
        
        for emp in sorted(missing_in_payroll, key=lambda x: x['name'])[:50]:
            try:
                print(f"{emp['id']:<15} {emp['name']:<40}")
            except:
                print(f"{emp['id']:<15} [Non-ASCII name]")

        if len(missing_in_payroll) > 50:
            print(f"\n... and {len(missing_in_payroll) - 50} more")

    print("\n" + "=" * 130)
    print("SUMMARY")
    print("=" * 130)
    print(f"\nPayroll Entity Breakdown:")
    for entity, count in sorted(entity_breakdown.items()):
        print(f"  {entity:<30} {count:>3} employees")
    
    print(f"\nCoverage:")
    coverage = (len(payroll_employees) - len(missing_in_insurance)) / len(payroll_employees) * 100 if payroll_employees else 0
    print(f"  Payroll employees with insurance: {len(payroll_employees) - len(missing_in_insurance)}/{len(payroll_employees)} ({coverage:.1f}%)")
    
if __name__ == "__main__":
    main()
