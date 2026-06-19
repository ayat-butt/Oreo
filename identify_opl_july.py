#!/usr/bin/env python3
"""Identify OPL employees in July 2024 file"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import pandas as pd
import io

def load_credentials():
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        if creds.expired:
            creds.refresh(Request())
        return creds
    except:
        return None

def main():
    creds = load_credentials()
    if not creds:
        return

    drive_service = build('drive', 'v3', credentials=creds)

    file_id = '1NLyPSfEO7N92EjGIBy6EnrrjvWmE7QTi'

    print("="*120)
    print("IDENTIFYING OPL EMPLOYEES IN JULY 2024")
    print("="*120)

    try:
        # Download and read
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()

        df = pd.read_excel(io.BytesIO(file_content), sheet_name='Payroll July - 2024')

        print(f"\nDataFrame shape: {len(df)} rows, {len(df.columns)} columns")
        print(f"\nAll columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i:2d}. {col}")

        # Check for entity/company/bank column
        print(f"\n\nLooking for entity/company identification columns...\n")
        print(f"First 20 rows of data:")
        print(df.head(20).to_string())

        # Look for any column that might contain "OPL" or "Orenda"
        print(f"\n\nSearching for OPL/Orenda mentions...\n")

        opl_employees = []
        for idx, row in df.iterrows():
            row_str = str(row).lower()
            if 'opl' in row_str or 'orenda' in row_str:
                print(f"Row {idx}: {row.to_dict()}")
                opl_employees.append(row)

        if opl_employees:
            print(f"\n\nFound {len(opl_employees)} rows with OPL/Orenda mention")
        else:
            print(f"\n\nNo rows found with OPL/Orenda mention")

            # Show all unique values in potential entity columns
            print(f"\n\nUnique values in potential entity columns:")
            for col in df.columns:
                col_lower = str(col).lower()
                if 'bank' in col_lower or 'entity' in col_lower or 'company' in col_lower or 'division' in col_lower:
                    unique_vals = df[col].unique()
                    print(f"\n  {col}: {len(unique_vals)} unique values")
                    for val in unique_vals[:10]:
                        if pd.notna(val):
                            print(f"    - {val}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
