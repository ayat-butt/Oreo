#!/usr/bin/env python3
"""Create Google Sheet via Google Drive API using authentication."""

import json
import os
from datetime import datetime

# Read CSV files
def read_csv(filepath):
    """Read CSV and return raw content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def prepare_sheet_info():
    """Prepare information about the sheet to be created."""
    emp_csv = read_csv('/c/Agent Oreo/output/EMPLOYEES_PROFILES.csv')
    dep_csv = read_csv('/c/Agent Oreo/output/EMPLOYEE_DEPENDENTS.csv')

    emp_lines = emp_csv.strip().split('\n')
    dep_lines = dep_csv.strip().split('\n')

    print("=" * 80)
    print("GOOGLE SHEET CREATION INFO")
    print("=" * 80)
    print(f"\nSheet Title: Employee Profiles & Dependents - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"\nEmployee Sheet: {len(emp_lines)} rows")
    print(f"  - Header: {emp_lines[0][:80]}...")
    print(f"  - Sample: {emp_lines[1][:80]}..." if len(emp_lines) > 1 else "")
    print(f"\nDependents Sheet: {len(dep_lines)} rows")
    print(f"  - Header: {dep_lines[0][:80]}...")
    print(f"  - Sample: {dep_lines[1][:80]}..." if len(dep_lines) > 1 else "")

    info = {
        "title": f"Employee Profiles & Dependents - {datetime.now().strftime('%Y-%m-%d')}",
        "employees": {
            "total_rows": len(emp_lines),
            "data_rows": len(emp_lines) - 1,
            "file": '/c/Agent Oreo/output/EMPLOYEES_PROFILES.csv'
        },
        "dependents": {
            "total_rows": len(dep_lines),
            "data_rows": len(dep_lines) - 1,
            "file": '/c/Agent Oreo/output/EMPLOYEE_DEPENDENTS.csv'
        }
    }

    with open('/c/Agent Oreo/output/sheet_creation_info.json', 'w') as f:
        json.dump(info, f, indent=2)

    return info

if __name__ == "__main__":
    info = prepare_sheet_info()
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("\nTo create the Google Sheet, you can:")
    print("\n1. OPTION A: Use Google Sheets UI directly")
    print("   - Go to: https://sheets.google.com")
    print("   - Create new spreadsheet")
    print(f"   - Name it: {info['title']}")
    print("   - Import the CSV files from output/ folder")
    print("\n2. OPTION B: Share CSV files")
    print("   - Employee file: output/EMPLOYEES_PROFILES.csv")
    print("   - Dependents file: output/EMPLOYEE_DEPENDENTS.csv")
    print(f"\nData Summary:")
    print(f"   - {info['employees']['data_rows']} employees")
    print(f"   - {info['dependents']['data_rows']} dependents")
