#!/usr/bin/env python3
"""Create properly formatted Google Sheet with employees and their dependents grouped together."""

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

def fetch_employees_with_dependents():
    """Fetch employees with their dependents grouped."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get employees
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
        WHERE cnic_number IS NOT NULL
        ORDER BY user_id
    """)

    employees = cur.fetchall()

    # Get all dependents
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

def create_grouped_sheet_data(employees, dependents_map):
    """Create sheet data with employees and their dependents grouped."""
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

        # Add employee row
        data.append([
            f"[EMP] {emp['user_id']}",  # Employee indicator
            emp['employee_id'] or "",
            emp['cnic_number'] or "",
            emp['marital_status'] or "",
            format_date(emp['date_of_birth']),
            emp['gender'] or "",
            emp['job_title'] or "",
            emp['department'] or "",
            emp['payroll_entity'] or "",
            emp['contact_number'] or "",
            emp['official_email'] or "",
            ""  # No relationship for employee
        ])

        # Add dependent rows below employee
        if emp_id in dependents_map:
            for dep in dependents_map[emp_id]:
                data.append([
                    f"  └─ {dep['dependent_name']}",  # Dependent indicator with indent
                    "",  # No employee ID for dependent
                    dep['cnic_number'] or "",
                    "",  # No marital status for dependent
                    format_date(dep['date_of_birth']),
                    "",  # No gender for dependent
                    "",  # No job title for dependent
                    "",  # No department for dependent
                    "",  # No entity for dependent
                    "",  # No contact for dependent
                    "",  # No email for dependent
                    dep['relationship'] or ""
                ])

        # Add blank row for spacing
        data.append([""] * 12)

    return data

def create_sheet_on_drive(data):
    """Create Google Sheet with the grouped data."""
    print("Loading Google credentials...")
    creds = load_google_credentials()
    if not creds:
        print("[ERROR] Could not load credentials")
        return None

    service = build('sheets', 'v4', credentials=creds)

    print("Creating Google Sheet...")
    title = f"Employee Profiles & Dependents - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

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
        'rows': len(data)
    }

def main():
    print("\n" + "=" * 80)
    print("CREATING GROUPED EMPLOYEE & DEPENDENTS SHEET")
    print("=" * 80 + "\n")

    print("Fetching data from Markaz...")
    employees, dependents_map = fetch_employees_with_dependents()
    print(f"[OK] Fetched {len(employees)} employees")

    total_deps = sum(len(deps) for deps in dependents_map.values())
    print(f"[OK] Fetched {total_deps} dependents")

    print("\nCreating grouped data structure...")
    data = create_grouped_sheet_data(employees, dependents_map)
    print(f"[OK] Created {len(data)} rows (including headers and spacing)")

    print("\nCreating Google Sheet on Drive...")
    result = create_sheet_on_drive(data)

    if result:
        print("\n" + "=" * 80)
        print("SUCCESS! SHEET CREATED")
        print("=" * 80)
        print(f"\nSheet URL: {result['sheet_url']}")
        print(f"Sheet ID: {result['sheet_id']}")
        print(f"Title: {result['title']}")
        print(f"Total Rows: {result['rows']}")

        # Save link to file
        with open('c:/Agent Oreo/output/final_sheet_link.txt', 'w') as f:
            f.write(f"Employee & Dependents Sheet\n")
            f.write(f"={'=' * 50}\n\n")
            f.write(f"URL: {result['sheet_url']}\n")
            f.write(f"Sheet ID: {result['sheet_id']}\n\n")
            f.write(f"Structure:\n")
            f.write(f"- Each employee listed with all their details\n")
            f.write(f"- Dependents immediately below the employee\n")
            f.write(f"- Total: {len(employees)} employees + {total_deps} dependents\n")

        print("\nLink saved to: output/final_sheet_link.txt")
    else:
        print("\n[ERROR] Failed to create sheet")

if __name__ == "__main__":
    main()
