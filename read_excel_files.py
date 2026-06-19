#!/usr/bin/env python3
"""Read Excel files from Google Drive links"""

import requests
import pandas as pd
from io import BytesIO
import json

def read_excel_from_google_drive(sheet_id, month):
    """Download and read Excel file from Google Drive"""
    try:
        # Construct direct download URL
        download_url = f"https://docs.google.com/spreadsheets/export?id={sheet_id}&exportFormat=xlsx"

        print(f"\nDownloading {month} data...")
        response = requests.get(download_url, timeout=30)

        if response.status_code == 200:
            # Read Excel file
            excel_file = BytesIO(response.content)

            # Try to read all sheets to find OPL data
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names

            print(f"  Sheet names found: {sheet_names}")

            # Look for OPL sheet or first sheet with data
            opl_data = None
            for sheet_name in sheet_names:
                if 'OPL' in sheet_name.upper():
                    opl_data = pd.read_excel(excel_file, sheet_name=sheet_name)
                    print(f"  Found OPL data in sheet: {sheet_name}")
                    break

            # If no OPL sheet, try first sheet
            if opl_data is None and len(sheet_names) > 0:
                opl_data = pd.read_excel(excel_file, sheet_name=sheet_names[0])
                print(f"  Reading first sheet: {sheet_names[0]}")

            if opl_data is not None:
                print(f"  Rows: {len(opl_data)}, Columns: {len(opl_data.columns)}")
                print(f"  Column names: {list(opl_data.columns)}")

                # Extract employee info
                employees = {}
                for col in opl_data.columns:
                    col_lower = str(col).lower()
                    if 'employee' in col_lower or 'name' in col_lower:
                        # Found name column
                        for idx, name in enumerate(opl_data[col]):
                            if pd.notna(name) and isinstance(name, str) and name.strip():
                                name = str(name).strip()
                                if len(name) > 2 and not name.lower().startswith('total'):
                                    employees[name] = idx
                        break

                print(f"  Found {len(employees)} employee records")

                # Show first few
                if employees:
                    print(f"  First 5 employees:")
                    for i, (name, idx) in enumerate(list(employees.items())[:5]):
                        print(f"    {i+1}. {name}")

                return employees
            else:
                print(f"  No data found in Excel file")
                return {}
        else:
            print(f"  Failed to download: HTTP {response.status_code}")
            return {}

    except Exception as e:
        print(f"  Error reading {month}: {e}")
        import traceback
        traceback.print_exc()
        return {}

# Sheet IDs from the provided links
sheets = {
    'July 2024': '1tIKIU0LKCR2YYuCS0u0lb_Gr-rDm6ks_',
    'August 2024': '15n2DllSdSDErWwl0pj3PkeqwJKF5LDbZ',
    'September 2024': '1bP1Ju0vzcS7QxF1NkheVZpI6HxliE-F7',
    'October 2024': '1h1IRXwxx-mRAp0m2C2sqHlIjR5OzYpjc',
}

print("="*80)
print("ATTEMPTING TO READ EXCEL FILES FROM GOOGLE DRIVE")
print("="*80)

for month, sheet_id in sheets.items():
    employees = read_excel_from_google_drive(sheet_id, month)
