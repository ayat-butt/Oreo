#!/usr/bin/env python3
"""Create clean, organized insurance sheet by Entity then Employee Name."""

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

def fetch_organized_data():
    """Fetch ALL current active employees organized by entity."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get ALL current employees organized by entity then name
    cur.execute("""
        SELECT
            ep.id,
            ep.user_id,
            COALESCE(u.first_name || ' ' || u.last_name, ep.user_id) as full_name,
            u.first_name,
            u.last_name,
            ep.employee_id,
            ep.cnic_number,
            ep.marital_status,
            ep.date_of_birth,
            ep.father_husband_name,
            ep.gender,
            ep.job_title,
            ep.department,
            ep.payroll_entity,
            ep.contact_number,
            ep.official_email,
            ep.joining_date,
            ep.bank_name,
            ep.bank_account_number,
            ep.bank_account_title
        FROM employee_profiles ep
        LEFT JOIN users u ON ep.user_id = u.id
        WHERE ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        ORDER BY ep.payroll_entity, COALESCE(u.first_name || ' ' || u.last_name, ep.user_id)
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

def create_clean_organized_data(employees, dependents_map):
    """Create clean, organized sheet data by Entity then Name."""
    data = []

    # Main Header
    data.append([
        "EMPLOYEE NAME",
        "Employee ID",
        "CNIC",
        "DOB",
        "Gender",
        "Marital Status",
        "Father/Husband",
        "Job Title",
        "Department",
        "Entity",
        "Joining Date",
        "Contact",
        "Email",
        "Bank Name",
        "Bank Account #",
        "Account Title",
        "Dependents/Relationship"
    ])

    # Group by entity
    entities_order = ['OPL', 'OWT', 'NIETE ICT', 'NIETE Islamabad', 'NIETE Balochistan', 'NIETE Rawalpindi']
    employees_by_entity = {}

    for emp in employees:
        entity = emp['payroll_entity'] or 'Other'
        if entity not in employees_by_entity:
            employees_by_entity[entity] = []
        employees_by_entity[entity].append(emp)

    # Process each entity
    for entity in entities_order:
        if entity not in employees_by_entity:
            continue

        # Entity header
        data.append([f"\n{entity.upper()}", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
        data.append(["=" * 50, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])

        # Process employees in this entity (already sorted by name from query)
        for emp in employees_by_entity[entity]:
            emp_id = emp['id']

            # Employee row
            data.append([
                emp['full_name'] or "",
                emp['employee_id'] or "",
                emp['cnic_number'] or "",
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

            # Add dependents below employee
            if emp_id in dependents_map:
                for dep in dependents_map[emp_id]:
                    data.append([
                        f"  └─ {dep['dependent_name']}",
                        "",
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

            # Spacing between employees
            data.append(["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])

    return data

def create_sheet_on_drive(data, emp_count, dep_count):
    """Create Google Sheet."""
    print("Loading Google credentials...")
    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not load credentials")
        return None

    service = build('sheets', 'v4', credentials=creds)

    print("Creating Google Sheet...")
    title = f"Insurance - All Active Employees (Organized) - {datetime.now().strftime('%Y-%m-%d')}"

    spreadsheet = {'properties': {'title': title}}

    result = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
    sheet_id = result['spreadsheetId']
    sheet_url = result['spreadsheetUrl']

    print(f"[OK] Sheet created: {sheet_id}")

    print(f"Populating with {len(data)} rows...")
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Sheet1!A1',
        valueInputOption='USER_ENTERED',
        body={'values': data}
    ).execute()

    print("[OK] Data populated")

    # Format main header
    print("Formatting header...")
    requests = [
        {
            'repeatCell': {
                'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.1, 'green': 0.3, 'blue': 0.6},
                        'textFormat': {
                            'bold': True,
                            'fontSize': 12,
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
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': [{
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 17
                }
            }
        }]}
    ).execute()

    return {
        'sheet_id': sheet_id,
        'sheet_url': sheet_url,
        'title': title,
        'rows': len(data),
        'employees': emp_count,
        'dependents': dep_count
    }

def main():
    print("\n" + "=" * 100)
    print("CREATING CLEAN, ORGANIZED INSURANCE SHEET")
    print("=" * 100 + "\n")

    print("Fetching employees (organized by entity, then name)...")
    employees, dependents_map = fetch_organized_data()
    emp_count = len(employees)
    dep_count = sum(len(deps) for deps in dependents_map.values())

    print(f"[OK] Fetched {emp_count} active employees")
    print(f"[OK] Fetched {dep_count} dependents")

    print("\nCreating clean, organized sheet data...")
    data = create_clean_organized_data(employees, dependents_map)
    print(f"[OK] Created {len(data)} rows with proper formatting")

    print("\nCreating Google Sheet...")
    result = create_sheet_on_drive(data, emp_count, dep_count)

    if result:
        print("\n" + "=" * 120)
        print("SUCCESS! CLEAN ORGANIZED SHEET CREATED")
        print("=" * 120)
        print(f"\nSheet URL: {result['sheet_url']}")
        print(f"Sheet ID: {result['sheet_id']}")
        print(f"\nOrganization:")
        print(f"  - By Entity (OPL, OWT, NIETE Islamabad, NIETE Balochistan, etc.)")
        print(f"  - Alphabetically by Employee Name within each entity")
        print(f"  - Dependents grouped with their employee")
        print(f"\nData Summary:")
        print(f"  - Active Employees: {result['employees']}")
        print(f"  - Dependents: {result['dependents']}")
        print(f"  - Total Rows: {result['rows']}")
        print(f"\nExcluded: Alumni and Resigned employees")
    else:
        print("\n[ERROR] Failed to create sheet")

if __name__ == "__main__":
    main()
