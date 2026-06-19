#!/usr/bin/env python3
"""Reorganize insurance data into template format with proper employee/dependent structure."""

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

def parse_insurance_data(values):
    """Parse insurance data and organize into employees with dependents."""
    employees = {}
    current_employee = None

    for row in values[1:]:  # Skip header
        if not row or all(not cell for cell in row):
            continue

        emp_id = row[0].strip() if len(row) > 0 and row[0] else ""
        emp_name = row[1].strip() if len(row) > 1 and row[1] else ""
        dependent_rel = row[2].strip() if len(row) > 2 and row[2] else ""
        marital_status = row[3].strip() if len(row) > 3 and row[3] else ""
        cnic = row[4].strip() if len(row) > 4 and row[4] else ""
        dob = row[5].strip() if len(row) > 5 and row[5] else ""
        gender = row[6].strip() if len(row) > 6 and row[6] else ""
        father_husband = row[7].strip() if len(row) > 7 and row[7] else ""
        entity = row[8].strip() if len(row) > 8 and row[8] else ""
        email = row[9].strip() if len(row) > 9 and row[9] else ""
        bank = row[10].strip() if len(row) > 10 and row[10] else ""
        account = row[11].strip() if len(row) > 11 and row[11] else ""

        # Skip section headers
        if emp_name in ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_', 'NIETE ISLAMABAD', 'NIETE BALOCHISTAN']:
            continue

        # If has employee ID, it's an employee record
        if emp_id and emp_name:
            employees[emp_id] = {
                'name': emp_name,
                'cnic': cnic,
                'dob': dob,
                'gender': gender,
                'marital_status': marital_status,
                'father_husband': father_husband,
                'entity': entity,
                'email': email,
                'bank': bank,
                'account': account,
                'dependents': []
            }
            current_employee = emp_id

        # If has dependent relation and current employee, it's a dependent
        elif dependent_rel and current_employee and emp_name:
            employees[current_employee]['dependents'].append({
                'name': emp_name,
                'cnic': cnic,
                'dob': dob,
                'relation': dependent_rel
            })

    return employees

def create_template_format_data(employees):
    """Convert employees dict to template format rows."""
    rows = []

    # Add header
    rows.append([
        'Employee Name',
        'CNIC',
        'Insured Person Name',
        'Relation',
        'DOB',
        'Health insurance Plan category',
        'Life insurance Plan category',
        'OPD Plan',
        'Bank Name',
        'Account Number'
    ])

    # Process each employee and their dependents
    for emp_id in sorted(employees.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        emp = employees[emp_id]

        # Add employee row (Self)
        rows.append([
            emp['name'],           # Employee Name
            emp['cnic'],           # CNIC
            emp['name'],           # Insured Person Name (same as employee)
            'Self',                # Relation
            emp['dob'],            # DOB
            '',                    # Health insurance Plan category (to be filled)
            '',                    # Life insurance Plan category (optional)
            '',                    # OPD Plan (optional)
            emp['bank'],           # Bank Name
            emp['account']         # Account Number
        ])

        # Add dependent rows
        for dep in emp['dependents']:
            rows.append([
                emp['name'],           # Employee Name (repeated)
                '',                    # CNIC (blank for dependents)
                dep['name'],           # Insured Person Name (dependent name)
                dep['relation'],       # Relation (Wife, Son, Daughter, etc.)
                dep['dob'],            # DOB
                '',                    # Health insurance Plan category (optional for dependents)
                '',                    # Life insurance Plan category (optional)
                '',                    # OPD Plan (optional)
                '',                    # Bank Name (blank for dependents)
                ''                     # Account Number (blank for dependents)
            ])

    return rows

def main():
    print("\n" + "=" * 130)
    print("REORGANIZING INSURANCE DATA TO TEMPLATE FORMAT")
    print("=" * 130 + "\n")

    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    # Read source data
    print("Reading insurance data from source sheet...")
    new_sheet_id = '1dLSkk_j8d8crKAGaZ8GWE1Jtf1Y0KOivvXUHYVeAJrM'

    result = service.spreadsheets().values().get(
        spreadsheetId=new_sheet_id,
        range="'Insurance Data 2026'!A:L"
    ).execute()

    values = result.get('values', [])
    print(f"[OK] Read {len(values)} rows\n")

    # Parse into employees with dependents
    print("Parsing employees and dependents...")
    employees = parse_insurance_data(values)
    total_employees = len(employees)
    total_dependents = sum(len(emp['dependents']) for emp in employees.values())
    total_records = total_employees + total_dependents

    print(f"[OK] Parsed {total_employees} employees")
    print(f"[OK] Parsed {total_dependents} dependents")
    print(f"[OK] Total records to create: {total_records}\n")

    # Create template format data
    print("Creating template format...")
    template_rows = create_template_format_data(employees)
    print(f"[OK] Created {len(template_rows)} rows (including header)\n")

    # Create new sheet or clear existing one
    print("Setting up destination sheet...")
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'

    try:
        # Clear the existing sheet
        service.spreadsheets().values().clear(
            spreadsheetId=insurance_sheet_id,
            range="'Insurance Data 2026'!A:J"
        ).execute()
        print("[OK] Cleared existing data\n")
    except Exception as e:
        print(f"[WARNING] Could not clear sheet: {e}\n")

    # Write template format data
    print("Writing reorganized data to Insurance sheet...")
    try:
        service.spreadsheets().values().update(
            spreadsheetId=insurance_sheet_id,
            range="'Insurance Data 2026'!A1",
            valueInputOption='USER_ENTERED',
            body={'values': template_rows}
        ).execute()

        print("[OK] Data written successfully!\n")

        print("=" * 130)
        print("REORGANIZATION COMPLETE")
        print("=" * 130)
        print(f"\nSheet Structure (New Template Format):")
        print(f"  Column A: Employee Name")
        print(f"  Column B: CNIC")
        print(f"  Column C: Insured Person Name")
        print(f"  Column D: Relation")
        print(f"  Column E: DOB")
        print(f"  Column F: Health insurance Plan category [EMPTY - TO BE FILLED]")
        print(f"  Column G: Life insurance Plan category [OPTIONAL]")
        print(f"  Column H: OPD Plan [OPTIONAL]")
        print(f"  Column I: Bank Name")
        print(f"  Column J: Account Number")

        print(f"\nData Summary:")
        print(f"  Total Employees: {total_employees}")
        print(f"  Total Dependents: {total_dependents}")
        print(f"  Total Records: {total_records}")
        print(f"  Total Rows in Sheet: {len(template_rows)} (including header)")

        print(f"\nSheet: https://docs.google.com/spreadsheets/d/1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s/edit")

    except Exception as e:
        print(f"[ERROR] Failed to write data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
