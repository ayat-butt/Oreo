#!/usr/bin/env python3
"""Extract data from old sheet, fill missing data in Markaz sheet, create reference tab."""

import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from difflib import SequenceMatcher

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
        print(f"Error: {e}")
        return None

def read_old_insurance_sheet():
    """Read the old insurance sheet."""
    print("Reading old insurance sheet...")
    creds = load_google_credentials()
    if not creds:
        return None

    service = build('sheets', 'v4', credentials=creds)
    old_sheet_id = '1HjyeoWzsxkC_t2yzPgSn6qb_huvNYq7qvzHB2m-AxHI'

    try:
        metadata = service.spreadsheets().get(spreadsheetId=old_sheet_id).execute()
        sheets = metadata.get('sheets', [])

        sheet_name = None
        for sheet in sheets:
            if sheet['properties']['sheetId'] == 195402472:
                sheet_name = sheet['properties']['title']
                break

        if not sheet_name:
            sheet_name = sheets[0]['properties']['title']

        result = service.spreadsheets().values().get(
            spreadsheetId=old_sheet_id,
            range=f'{sheet_name}'
        ).execute()

        values = result.get('values', [])
        print(f"[OK] Read {len(values)} rows from old sheet\n")
        return values
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def parse_old_sheet_data(values):
    """Parse old sheet to extract employee data."""
    if not values or len(values) < 2:
        return {}

    headers = values[0]
    old_data = {}

    for row in values[1:]:
        if not row or len(row) < 2:
            continue

        emp_name = row[0].strip() if row[0] else None
        cnic = row[1].strip() if len(row) > 1 and row[1] else None
        insured_name = row[2].strip() if len(row) > 2 and row[2] else None
        relation = row[3].strip() if len(row) > 3 and row[3] else None
        dob = row[4].strip() if len(row) > 4 and row[4] else None

        if emp_name:
            emp_key = emp_name.lower()
            if emp_key not in old_data:
                old_data[emp_key] = {
                    'name': emp_name,
                    'cnic': cnic,
                    'dob': dob,
                    'dependents': []
                }

            if insured_name and insured_name != emp_name:
                old_data[emp_key]['dependents'].append({
                    'name': insured_name,
                    'relation': relation,
                    'dob': dob if insured_name != emp_name else None
                })

    print(f"[OK] Parsed {len(old_data)} employees from old sheet")
    return old_data

def get_markaz_employees():
    """Get Markaz employees."""
    print("Fetching Markaz employees...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            ep.id,
            ep.user_id,
            COALESCE(u.first_name || ' ' || u.last_name, ep.user_id) as full_name,
            u.first_name,
            u.last_name,
            ep.employee_id,
            ep.cnic_number,
            ep.date_of_birth,
            ep.payroll_entity
        FROM employee_profiles ep
        LEFT JOIN users u ON ep.user_id = u.id
        WHERE ep.compensation_status NOT IN ('Alumni', 'Resigned', 'ALUMNI', 'RESIGNED')
        ORDER BY COALESCE(u.first_name || ' ' || u.last_name, ep.user_id)
    """)

    employees = cur.fetchall()
    conn.close()

    print(f"[OK] Fetched {len(employees)} Markaz employees\n")
    return employees

def match_employees(markaz_emps, old_data):
    """Match Markaz employees with old sheet data."""
    print("Matching employees...")
    matches = []

    for emp in markaz_emps:
        emp_name_lower = emp['full_name'].lower() if emp['full_name'] else ""

        # Try exact match first
        if emp_name_lower in old_data:
            matches.append({
                'markaz': emp,
                'old': old_data[emp_name_lower],
                'match_type': 'exact',
                'confidence': 1.0
            })
        else:
            # Try fuzzy match
            best_match = None
            best_score = 0

            for old_name, old_info in old_data.items():
                score = SequenceMatcher(None, emp_name_lower, old_name).ratio()
                if score > best_score and score > 0.85:
                    best_score = score
                    best_match = old_info

            if best_match:
                matches.append({
                    'markaz': emp,
                    'old': best_match,
                    'match_type': 'fuzzy',
                    'confidence': best_score
                })

    print(f"[OK] Matched {len(matches)} employees\n")
    return matches

def identify_missing_data(matches):
    """Identify what data can be filled."""
    print("Identifying missing data...")

    to_fill = []
    reference_data = []

    for match in matches:
        m_emp = match['markaz']
        o_emp = match['old']

        # Check what's missing in Markaz but available in old sheet
        markaz_has_cnic = m_emp['cnic_number'] and m_emp['cnic_number'].strip()
        markaz_has_dob = m_emp['date_of_birth']
        old_has_cnic = o_emp['cnic']
        old_has_dob = o_emp['dob']

        if (not markaz_has_cnic and old_has_cnic) or (not markaz_has_dob and old_has_dob):
            to_fill.append({
                'id': m_emp['id'],
                'user_id': m_emp['user_id'],
                'name': m_emp['full_name'],
                'emp_id': m_emp['employee_id'],
                'fill_cnic': not markaz_has_cnic and old_has_cnic,
                'new_cnic': old_has_cnic,
                'old_cnic': o_emp['cnic'],
                'fill_dob': not markaz_has_dob and old_has_dob,
                'new_dob': old_has_dob,
                'old_dob': o_emp['dob'],
                'match_confidence': match['confidence']
            })

        # Add to reference
        reference_data.append({
            'markaz_name': m_emp['full_name'],
            'markaz_cnic': m_emp['cnic_number'] or '[MISSING]',
            'markaz_dob': str(m_emp['date_of_birth'])[:10] if m_emp['date_of_birth'] else '[MISSING]',
            'old_name': o_emp['name'],
            'old_cnic': o_emp['cnic'] or '[MISSING]',
            'old_dob': o_emp['dob'] or '[MISSING]',
            'dependents_count': len(o_emp['dependents']),
            'match_type': match['match_type'],
            'confidence': f"{match['confidence']*100:.0f}%"
        })

    print(f"[OK] Found {len(to_fill)} records with fillable data")
    print(f"[OK] Created {len(reference_data)} reference records\n")

    return to_fill, reference_data

def update_markaz_with_missing_data(to_fill):
    """Update Markaz with missing CNIC and DOB data."""
    print("Updating Markaz with missing data...")

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    updated_count = 0

    for record in to_fill:
        try:
            if record['fill_cnic'] and record['old_cnic']:
                cur.execute(
                    "UPDATE employee_profiles SET cnic_number = %s WHERE id = %s",
                    (record['old_cnic'], record['id'])
                )
                print(f"  [CNIC] {record['name']} <- {record['old_cnic']}")
                updated_count += 1

            if record['fill_dob'] and record['old_dob']:
                cur.execute(
                    "UPDATE employee_profiles SET date_of_birth = %s WHERE id = %s",
                    (record['old_dob'], record['id'])
                )
                print(f"  [DOB] {record['name']} <- {record['old_dob']}")
                updated_count += 1
        except Exception as e:
            print(f"  [ERROR] {record['name']}: {e}")

    conn.commit()
    conn.close()

    print(f"\n[OK] Updated {updated_count} records in Markaz\n")
    return updated_count

def create_reference_sheet(sheet_id, reference_data):
    """Create new sub-tab with reference data."""
    print("Creating reference sub-tab...")

    creds = load_google_credentials()
    if not creds:
        return False

    service = build('sheets', 'v4', credentials=creds)

    # Add new sheet
    try:
        requests = [{
            'addSheet': {
                'properties': {
                    'title': 'Data from Old Insurance Sheet'
                }
            }
        }]

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()

        print("[OK] Created new sub-tab")

        # Prepare data for the new sheet
        headers = [
            'Markaz Employee Name',
            'Markaz CNIC',
            'Markaz DOB',
            'Old Sheet Name',
            'Old Sheet CNIC',
            'Old Sheet DOB',
            'Dependents (Old Sheet)',
            'Match Type',
            'Confidence %'
        ]

        data = [headers]
        for ref in reference_data:
            data.append([
                ref['markaz_name'],
                ref['markaz_cnic'],
                ref['markaz_dob'],
                ref['old_name'],
                ref['old_cnic'],
                ref['old_dob'],
                ref['dependents_count'],
                ref['match_type'],
                ref['confidence']
            ])

        # Write data
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="'Data from Old Insurance Sheet'!A1",
            valueInputOption='USER_ENTERED',
            body={'values': data}
        ).execute()

        print(f"[OK] Added {len(reference_data)} reference records")

        # Format header
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 1,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.8, 'green': 0.6, 'blue': 0.2},
                        'textFormat': {
                            'bold': True,
                            'fontSize': 11,
                            'foregroundColor': {'red': 0, 'green': 0, 'blue': 0}
                        }
                    }
                },
                'fields': 'userEnteredFormat'
            }
        }]

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()

        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 100)
    print("EXTRACTING DATA FROM OLD SHEET & UPDATING MARKAZ")
    print("=" * 100 + "\n")

    # Step 1: Read old sheet
    old_values = read_old_insurance_sheet()
    if not old_values:
        print("[ERROR] Could not read old sheet")
        return

    # Step 2: Parse old sheet
    old_data = parse_old_sheet_data(old_values)

    # Step 3: Get Markaz employees
    markaz_emps = get_markaz_employees()

    # Step 4: Match employees
    matches = match_employees(markaz_emps, old_data)

    # Step 5: Identify missing data
    to_fill, reference_data = identify_missing_data(matches)

    # Step 6: Update Markaz
    if to_fill:
        updated = update_markaz_with_missing_data(to_fill)
        print(f"Updated: {updated} fields in Markaz database\n")
    else:
        print("[INFO] No data to fill - all fields already complete\n")

    # Step 7: Create reference sheet
    sheet_id = '1JNAccMOxozFO3BbCapxgiP2MN5HDpizlfQ6WfQVHc4s'
    if create_reference_sheet(sheet_id, reference_data):
        print("[OK] Reference sheet created successfully")

    print("\n" + "=" * 100)
    print("COMPLETE")
    print("=" * 100)
    print(f"\nUpdated Markaz: {len(to_fill) if to_fill else 0} records")
    print(f"Created Reference Tab: 'Data from Old Insurance Sheet'")
    print(f"Total Reference Records: {len(reference_data)}")
    print("\nMain sheet: UNCHANGED (clean & organized)")
    print("Reference sheet: New data for your review")

if __name__ == "__main__":
    main()
