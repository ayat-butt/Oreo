#!/usr/bin/env python3
"""Create ULTIMATE COMPLETE sheet with ALL 246 employees (with & without CNIC) + 123 dependents."""

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

def fetch_all_employees_and_dependents():
    """Fetch ALL employees (246: with & without CNIC) and ALL dependents (123)."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get ALL current employees (including those without CNIC)
    cur.execute("""
        SELECT
            id,
            user_id,
            employee_id,
            cnic_number,
            marital_status,
            date_of_birth,
            gender,
            job_title,
            department,
            payroll_entity,
            contact_number,
            official_email
        FROM employee_profiles
        WHERE compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        ORDER BY user_id
    """)

    employees = cur.fetchall()

    # Get ALL dependents for employees WITH CNIC only
    cur.execute("""
        SELECT
            d.employee_profile_id,
            d.name as dependent_name,
            d.relationship,
            d.date_of_birth,
            d.cnic_number
        FROM dependents d
        JOIN employee_profiles ep ON d.employee_profile_id = ep.id
        WHERE ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
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

def create_ultimate_grouped_data(employees, dependents_map):
    """Create sheet data with ALL 246 employees and ALL dependents grouped."""
    data = []

    # Header
    data.append([
        "EMPLOYEE/DEPENDENT",
        "Employee ID",
        "CNIC",
        "Marital Status",
        "Date of Birth",
        "Gender",
        "Job Title",
        "Department",
        "Entity",
        "Contact Number",
        "Email",
        "Relationship"
    ])

    # Process each employee with their dependents
    for emp in employees:
        emp_id = emp['id']
        has_cnic = emp['cnic_number'] and emp['cnic_number'].strip() != ''

        # Add employee row
        emp_indicator = "[EMP]" if has_cnic else "[EMP-NO-CNIC]"
        data.append([
            f"{emp_indicator} {emp['user_id']}",
            emp['employee_id'] or "",
            emp['cnic_number'] or "[PENDING]",
            emp['marital_status'] or "",
            format_date(emp['date_of_birth']),
            emp['gender'] or "",
            emp['job_title'] or "",
            emp['department'] or "",
            emp['payroll_entity'] or "",
            emp['contact_number'] or "",
            emp['official_email'] or "",
            ""
        ])

        # Add dependent rows below employee (only if they have CNIC)
        if has_cnic and emp_id in dependents_map:
            for dep in dependents_map[emp_id]:
                data.append([
                    f"  └─ {dep['dependent_name']}",
                    "",
                    dep['cnic_number'] or "",
                    "",
                    format_date(dep['date_of_birth']),
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    dep['relationship'] or ""
                ])

        # Add blank row for spacing
        data.append([""] * 12)

    return data

def create_sheet_on_drive(data, total_emp, emp_with_cnic, emp_without_cnic, dep_count):
    """Create Google Sheet with the ultimate grouped data."""
    print("Loading Google credentials...")
    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not load credentials")
        return None

    service = build('sheets', 'v4', credentials=creds)

    print("Creating Google Sheet...")
    title = f"Employee Profiles & Dependents - ULTIMATE COMPLETE - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

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
                        'backgroundColor': {'red': 0.15, 'green': 0.15, 'blue': 0.5},
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
                    'endIndex': 12
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
        'total_employees': total_emp,
        'employees_with_cnic': emp_with_cnic,
        'employees_without_cnic': emp_without_cnic,
        'dependents': dep_count
    }

def main():
    print("\n" + "=" * 100)
    print("CREATING ULTIMATE COMPLETE SHEET - ALL 246 EMPLOYEES + 123 DEPENDENTS")
    print("=" * 100 + "\n")

    print("Fetching data from Markaz...")
    employees, dependents_map = fetch_all_employees_and_dependents()
    total_emp = len(employees)
    emp_with_cnic = sum(1 for e in employees if e['cnic_number'] and e['cnic_number'].strip())
    emp_without_cnic = total_emp - emp_with_cnic
    dep_count = sum(len(deps) for deps in dependents_map.values())

    print(f"[OK] Fetched {total_emp} total employees")
    print(f"     - {emp_with_cnic} with CNIC (profile complete)")
    print(f"     - {emp_without_cnic} without CNIC (haven't logged in yet)")
    print(f"[OK] Fetched {dep_count} dependents")

    print("\nCreating grouped data structure...")
    data = create_ultimate_grouped_data(employees, dependents_map)
    print(f"[OK] Created {len(data)} rows (including headers and spacing)")

    print("\nCreating Google Sheet on Drive...")
    result = create_sheet_on_drive(data, total_emp, emp_with_cnic, emp_without_cnic, dep_count)

    if result:
        print("\n" + "=" * 120)
        print("SUCCESS! ULTIMATE COMPLETE SHEET CREATED")
        print("=" * 120)
        print(f"\nSheet URL: {result['sheet_url']}")
        print(f"Sheet ID: {result['sheet_id']}")
        print(f"Title: {result['title']}")
        print(f"\nData Summary:")
        print(f"  [OK] Total Employees: {result['total_employees']}")
        print(f"       - With CNIC: {result['employees_with_cnic']}")
        print(f"       - Without CNIC: {result['employees_without_cnic']} (haven't logged in)")
        print(f"  [OK] Total Dependents: {result['dependents']}")
        print(f"  [OK] Total Rows: {result['rows']}")

        # Save link to file
        with open('c:/Agent Oreo/output/ULTIMATE_COMPLETE_SHEET_LINK.txt', 'w') as f:
            f.write(f"ULTIMATE COMPLETE Employee & Dependents Sheet\n")
            f.write(f"{'=' * 70}\n\n")
            f.write(f"URL: {result['sheet_url']}\n")
            f.write(f"Sheet ID: {result['sheet_id']}\n\n")
            f.write(f"Data Summary:\n")
            f.write(f"  Total Employees: {result['total_employees']}\n")
            f.write(f"    - With CNIC (profile complete): {result['employees_with_cnic']}\n")
            f.write(f"    - Without CNIC (haven't logged in): {result['employees_without_cnic']}\n")
            f.write(f"  Total Dependents: {result['dependents']}\n\n")
            f.write(f"Legend:\n")
            f.write(f"  [EMP] = Employee with complete profile (CNIC filled)\n")
            f.write(f"  [EMP-NO-CNIC] = Employee without CNIC (hasn't logged in yet)\n")
            f.write(f"  └─ = Dependent of the employee above\n\n")
            f.write(f"Excluded: Alumni and Resigned employees\n")

        print("\nLink saved to: output/ULTIMATE_COMPLETE_SHEET_LINK.txt")
    else:
        print("\n[ERROR] Failed to create sheet")

if __name__ == "__main__":
    main()
