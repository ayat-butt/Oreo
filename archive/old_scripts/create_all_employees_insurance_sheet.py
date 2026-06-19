#!/usr/bin/env python3
"""Create COMPLETE insurance sheet with ALL 246 employees (no filtering, all data levels)."""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

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
        print(f"Error loading credentials: {e}")
        return None

def fetch_all_current_employees_and_dependents():
    """Fetch ALL current employees (no filtering) and ALL dependents."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get ALL current employees - NO CNIC filtering
    cur.execute("""
        SELECT
            id,
            user_id,
            employee_id,
            cnic_number,
            marital_status,
            date_of_birth,
            father_husband_name,
            gender,
            job_title,
            department,
            payroll_entity,
            contact_number,
            official_email,
            joining_date,
            bank_name,
            bank_account_number,
            bank_account_title
        FROM employee_profiles
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        ORDER BY payroll_entity, user_id
    """)

    employees = cur.fetchall()

    # Get ALL dependents
    cur.execute("""
        SELECT
            d.employee_profile_id,
            d.name as dependent_name,
            d.relationship,
            d.date_of_birth,
            d.cnic_number
        FROM dependents d
        ORDER BY d.employee_profile_id, d.name
    """)

    all_dependents = cur.fetchall()
    conn.close()

    # Group dependents by employee
    dependents_map = {}
    for dep in all_dependents:
        emp_id = dep['employee_profile_id']
        if emp_id not in dependents_map:
            dependents_map[emp_id] = []
        dependents_map[emp_id].append(dep)

    return list(employees), dependents_map

def format_date(date_obj):
    """Format date for display."""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return str(date_obj)[:10]

def create_insurance_sheet_data(employees, dependents_map):
    """Create sheet data for insurance - all employees with all details."""
    data = []

    # Header with comprehensive columns for insurance
    data.append([
        "EMPLOYEE/DEPENDENT",
        "Employee ID",
        "Full Name (user_id)",
        "CNIC",
        "DOB",
        "Gender",
        "Marital Status",
        "Father/Husband Name",
        "Job Title",
        "Department",
        "Entity",
        "Joining Date",
        "Contact Number",
        "Email",
        "Bank Name",
        "Bank Account #",
        "Account Title",
        "Relationship"
    ])

    # Process each employee with their dependents
    for emp in employees:
        emp_id = emp['id']
        has_cnic = emp['cnic_number'] and emp['cnic_number'].strip() != ''

        # Add employee row
        emp_indicator = "[EMP]" if has_cnic else "[EMP-INCOMPLETE]"
        data.append([
            f"{emp_indicator} {emp['user_id']}",
            emp['employee_id'] or "",
            emp['user_id'] or "",
            emp['cnic_number'] or "[PENDING]",
            format_date(emp['date_of_birth']),
            emp['gender'] or "",
            emp['marital_status'] or "",
            emp['father_husband_name'] or "",
            emp['job_title'] or "",
            emp['department'] or "",
            emp['payroll_entity'] or "",
            format_date(emp['joining_date']),
            emp['contact_number'] or "",
            emp['official_email'] or "",
            emp['bank_name'] or "",
            emp['bank_account_number'] or "",
            emp['bank_account_title'] or "",
            ""
        ])

        # Add dependent rows below employee (if they have any)
        if emp_id in dependents_map:
            for dep in dependents_map[emp_id]:
                data.append([
                    f"  └─ {dep['dependent_name']}",
                    "",
                    dep['dependent_name'],
                    dep['cnic_number'] or "",
                    format_date(dep['date_of_birth']),
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    dep['relationship'] or ""
                ])

        # Add blank row for spacing
        data.append([""] * 18)

    return data

def create_sheet_on_drive(data, total_emp, dep_count):
    """Create Google Sheet."""
    print("Loading Google credentials...")
    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not load credentials")
        return None

    service = build('sheets', 'v4', credentials=creds)

    print("Creating Google Sheet...")
    title = f"INSURANCE - All Employees & Dependents - {datetime.now().strftime('%Y-%m-%d')}"

    spreadsheet = {
        'properties': {
            'title': title
        }
    }

    result = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
    sheet_id = result['spreadsheetId']
    sheet_url = result['spreadsheetUrl']

    print(f"[OK] Sheet created: {sheet_id}")

    print(f"Populating sheet with {len(data)} rows...")
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Sheet1!A1',
        valueInputOption='USER_ENTERED',
        body={'values': data}
    ).execute()

    print("[OK] Data populated")

    # Format header
    print("Formatting header...")
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.2},
                        'textFormat': {
                            'bold': True,
                            'fontSize': 11,
                            'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                        },
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat'
            }
        },
        {
            'updateSheetProperties': {
                'properties': {
                    'sheetId': 0,
                    'gridProperties': {'frozenRowCount': 1}
                },
                'fields': 'gridProperties.frozenRowCount'
            }
        }
    ]

    service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()

    # Auto-resize columns
    print("Resizing columns...")
    requests = [
        {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 18
                }
            }
        }
    ]

    service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()

    return {
        'sheet_id': sheet_id,
        'sheet_url': sheet_url,
        'title': title,
        'rows': len(data),
        'employees': total_emp,
        'dependents': dep_count
    }

def main():
    print("\n" + "=" * 100)
    print("CREATING INSURANCE SHEET - ALL 246 EMPLOYEES (COMPLETE & INCOMPLETE DATA)")
    print("=" * 100 + "\n")

    print("Fetching data from Markaz...")
    employees, dependents_map = fetch_all_current_employees_and_dependents()
    total_emp = len(employees)
    dep_count = sum(len(deps) for deps in dependents_map.values())

    print(f"[OK] Fetched {total_emp} TOTAL current employees (no filtering)")
    print(f"[OK] Fetched {dep_count} dependents")

    print("\nCreating insurance sheet data...")
    data = create_insurance_sheet_data(employees, dependents_map)
    print(f"[OK] Created {len(data)} rows")

    print("\nCreating Google Sheet on Drive...")
    result = create_sheet_on_drive(data, total_emp, dep_count)

    if result:
        print("\n" + "=" * 120)
        print("SUCCESS! INSURANCE SHEET CREATED WITH ALL EMPLOYEES")
        print("=" * 120)
        print(f"\nSheet URL: {result['sheet_url']}")
        print(f"Sheet ID: {result['sheet_id']}")
        print(f"\nData Summary:")
        print(f"  [OK] Total Employees: {result['employees']}")
        print(f"  [OK] Total Dependents: {result['dependents']}")
        print(f"  [OK] Total Rows: {result['rows']}")
        print(f"\n[OK] Includes ALL current employees - complete & incomplete data")
        print(f"[OK] Excluded: Alumni and Resigned employees only")
    else:
        print("\n[ERROR] Failed to create sheet")

if __name__ == "__main__":
    main()
