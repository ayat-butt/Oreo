#!/usr/bin/env python3
"""Read August, September, October 2024 data"""

import requests
import pandas as pd
from io import BytesIO

def read_sheet(sheet_id, month):
    try:
        download_url = f"https://docs.google.com/spreadsheets/export?id={sheet_id}&exportFormat=xlsx"
        print(f"\nTrying {month}...")
        response = requests.get(download_url, timeout=30)

        if response.status_code == 200:
            excel_file = BytesIO(response.content)
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names
            print(f"  Sheets: {sheet_names}")
            
            df = pd.read_excel(excel_file, sheet_name=sheet_names[0])
            print(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Find name column
            name_col = None
            for col in df.columns:
                if 'employee' in str(col).lower() or 'name' in str(col).lower():
                    name_col = col
                    break
            
            if name_col:
                names = [str(n).strip() for n in df[name_col] if pd.notna(n) and isinstance(n, str) and len(str(n).strip()) > 2]
                print(f"  Employees found: {len(names)}")
                return names
            return []
        else:
            print(f"  Failed: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"  Error: {e}")
        return []

sheets = {
    'August 2024': '1bZ6o7pAI1evbtnev_qy4pf1s9jzH54TR-lJiJNp9PBo',
    'September 2024': '1juP_a4Dw-rrkkYxY530MKixLB4--X9IgSQ3Rc5HpXXg',
    'October 2024': '1AJcq5ZDt1AF5MU8pg5NKf3onFz8IiH2bISIeuD9YMfI',
}

print("="*80)
print("READING AUGUST, SEPTEMBER, OCTOBER 2024")
print("="*80)

for month, sheet_id in sheets.items():
    read_sheet(sheet_id, month)
