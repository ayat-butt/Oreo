#!/usr/bin/env python3
"""Create detailed Google Sheet with employee profiles and dependents."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuth2Credentials
import pickle
from googleapiclient.discovery import build
from datetime import datetime
import json

load_dotenv()
DB_URL = os.getenv("MARKAZ_DB_URL")

def get_sheet_service():
    """Get Google Sheets service with proper authentication."""
    SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

    creds = None
    # Try to load existing token
    if os.path.exists('/c/Agent Oreo/token.json'):
        with open('/c/Agent Oreo/token.json', 'rb') as token_file:
            creds = pickle.load(token_file)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Error: Could not authenticate with Google Sheets")
            return None

    return build('sheets', 'v4', credentials=creds)

def fetch_employees():
    """Fetch all employees with profile data."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
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
            joining_date,
            contact_number,
            official_email,
            dependents as dependents_count
        FROM employee_profiles
        WHERE cnic_number IS NOT NULL
        ORDER BY user_id
    """)

    employees = cur.fetchall()
    conn.close()
    return employees

def fetch_dependents():
    """Fetch all dependents with employee info."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            ep.user_id,
            ep.employee_id,
            d.name as dependent_name,
            d.relationship,
            d.date_of_birth,
            d.cnic_number
        FROM dependents d
        JOIN employee_profiles ep ON d.employee_profile_id = ep.id
        ORDER BY ep.user_id, d.name
    """)

    dependents = cur.fetchall()
    conn.close()
    return dependents

def create_sheet(service, title):
    """Create a new Google Sheet and return its ID."""
    spreadsheet = {
        'properties': {
            'title': title,
        }
    }

    result = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
    return result.get('spreadsheetId')

def clear_sheet(service, sheet_id, range_name):
    """Clear a sheet range."""
    try:
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
    except:
        pass

def update_sheet(service, sheet_id, range_name, values, value_input_option='USER_ENTERED'):
    """Update sheet with values."""
    body = {
        'values': values
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption=value_input_option,
        body=body
    ).execute()

    return result

def format_date(date_obj):
    """Format date for display."""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return str(date_obj)[:10]

def main():
    print("\n" + "=" * 80)
    print("CREATING EMPLOYEE PROFILE & DEPENDENTS GOOGLE SHEET")
    print("=" * 80)

    # Get Google Sheets service
    print("\nAuthenticating with Google Sheets...")
    service = get_sheet_service()
    if not service:
        print("Failed to authenticate. Using local JSON export only.")
        return

    # Fetch data
    print("Fetching employee data...")
    employees = fetch_employees()
    print(f"  ✓ Fetched {len(employees)} employees")

    print("Fetching dependent data...")
    dependents = fetch_dependents()
    print(f"  ✓ Fetched {len(dependents)} dependents")

    # Create sheet
    print("\nCreating Google Sheet...")
    sheet_title = f"Employee Profiles & Dependents - {datetime.now().strftime('%Y-%m-%d')}"
    sheet_id = create_sheet(service, sheet_title)
    print(f"  ✓ Sheet created: {sheet_id}")

    # Prepare employee data
    print("\nPreparing employee data...")
    employee_rows = [
        [
            "Employee Name (user_id)",
            "Employee ID",
            "CNIC",
            "Marital Status",
            "Date of Birth",
            "Father/Husband Name",
            "Gender",
            "Job Title",
            "Department",
            "Entity",
            "Joining Date",
            "Contact Number",
            "Official Email",
            "Dependents Count"
        ]
    ]

    for emp in employees:
        employee_rows.append([
            emp['user_id'] or "",
            emp['employee_id'] or "",
            emp['cnic_number'] or "",
            emp['marital_status'] or "",
            format_date(emp['date_of_birth']),
            emp['father_husband_name'] or "",
            emp['gender'] or "",
            emp['job_title'] or "",
            emp['department'] or "",
            emp['payroll_entity'] or "",
            format_date(emp['joining_date']),
            emp['contact_number'] or "",
            emp['official_email'] or "",
            emp['dependents_count'] or "0"
        ])

    # Update employees sheet
    print(f"Updating Employee sheet ({len(employee_rows)} rows)...")
    clear_sheet(service, sheet_id, "Sheet1")
    update_sheet(service, sheet_id, "Sheet1", employee_rows)
    print("  ✓ Employee data updated")

    # Prepare dependent data
    print("\nPreparing dependent data...")
    dependent_rows = [
        [
            "Employee Name (user_id)",
            "Employee ID",
            "Dependent Name",
            "Relationship",
            "Date of Birth",
            "CNIC"
        ]
    ]

    for dep in dependents:
        dependent_rows.append([
            dep['user_id'] or "",
            dep['employee_id'] or "",
            dep['dependent_name'] or "",
            dep['relationship'] or "",
            format_date(dep['date_of_birth']),
            dep['cnic_number'] or ""
        ])

    # Add dependents sheet
    print(f"Creating Dependents sheet ({len(dependent_rows)} rows)...")
    body = {
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': 'Dependents'
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
    update_sheet(service, sheet_id, "Dependents", dependent_rows)
    print("  ✓ Dependent data updated")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Sheet created successfully!")
    print(f"✓ Total Employees: {len(employees)}")
    print(f"✓ Total Dependents: {len(dependents)}")
    print(f"\nGoogle Sheet ID: {sheet_id}")
    print(f"URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    # Also save local JSON
    print("\nSaving local backup...")
    export_data = {
        "extraction_date": datetime.now().isoformat(),
        "summary": {
            "total_employees": len(employees),
            "total_dependents": len(dependents)
        },
        "employees": [dict(e) for e in employees],
        "dependents": [dict(d) for d in dependents]
    }

    with open("c:\\Agent Oreo\\output\\employee_profiles_export.json", "w") as f:
        json.dump(export_data, f, indent=2, default=str)

    print("  ✓ Local backup saved to output/employee_profiles_export.json")

if __name__ == "__main__":
    main()
