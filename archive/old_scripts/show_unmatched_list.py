#!/usr/bin/env python3
"""Show all unmatched employees."""

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

def extract_payroll_data(service):
    """Get all payroll employee IDs and names."""
    payroll_sheet_id = '1kr1q79P6tU5BSep_OWfSkjtmPeI5Uk_5at4a-KMQzDk'
    entity_sheets = ['OPL', 'OWT', 'NIETE_Islamabad', 'NIETE_Balochistan', 'Taleemabad_Inc_']

    payroll_employees = set()

    for entity in entity_sheets:
        result = service.spreadsheets().values().get(
            spreadsheetId=payroll_sheet_id,
            range=f"'{entity}'!A:D"
        ).execute()

        values = result.get('values', [])

        for row in values[1:]:
            if row and len(row) > 1:
                emp_id = row[0].strip() if row[0] else ""
                emp_name = row[1].strip() if row[1] else ""
                if emp_id and emp_name:
                    payroll_employees.add(emp_name.lower())

    return payroll_employees

def main():
    creds = load_google_credentials()
    if not creds:
        return

    service = build('sheets', 'v4', credentials=creds)

    print("Getting unmatched employees...\n")

    # Get payroll data
    payroll_employees = extract_payroll_data(service)

    # Get insurance data
    insurance_sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'
    result = service.spreadsheets().values().get(
        spreadsheetId=insurance_sheet_id,
        range='Sheet1!A:D'
    ).execute()

    values = result.get('values', [])
    unmatched = []

    for idx, row in enumerate(values[1:], 1):
        if not row or not row[0]:
            continue

        col_a = row[0].strip() if row[0] else ""
        col_b = row[1].strip() if len(row) > 1 else ""
        col_c = row[2].strip() if len(row) > 2 else ""

        # Skip section headers
        if col_a.startswith('[') or col_a.startswith('=') or len(col_a) < 2:
            continue

        if col_b and col_b.lower() not in payroll_employees:
            unmatched.append({
                'name': col_b,
                'cnic': col_c,
                'row': idx + 1
            })

    print(f"Total Unmatched Employees: {len(unmatched)}\n")
    print(f"{'No':<5} {'Employee Name':<40} {'CNIC':<20}")
    print("-" * 70)

    for idx, emp in enumerate(unmatched, 1):
        try:
            print(f"{idx:<5} {emp['name']:<40} {emp['cnic']:<20}")
        except:
            print(f"{idx:<5} [Non-ASCII name] {emp['cnic']:<20}")

if __name__ == "__main__":
    main()
