#!/usr/bin/env python3
"""
Check the coordinate format used in the Buscaro tracker sheet.
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

BUSCARO_SPREADSHEET_ID = "12EyDg8UAuDFexpJ_oC7hCN2HU0lDuQbAHHkmbdFKJwQ"
BUSCARO_SHEET_ID = 997855889
RANGE = "A1:Z50"

def get_buscaro_format():
    """Check the Buscaro tracker format."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds:
        print("[ERROR] No authentication. Please run upload_coordinates.py first")
        return

    service = build('sheets', 'v4', credentials=creds)

    print("[FETCHING] Reading Buscaro tracker sheet...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=BUSCARO_SPREADSHEET_ID,
            range=RANGE
        ).execute()

        values = result.get('values', [])

        if not values:
            print("[ERROR] No data found")
            return

        headers = values[0]
        print(f"\n[COLUMNS FOUND]: {len(headers)}")
        for idx, col in enumerate(headers):
            print(f"  {idx}: {col}")

        # Look for coordinate columns
        print("\n[SAMPLE DATA]:")
        for row_idx in range(1, min(6, len(values))):
            row = values[row_idx]
            print(f"\nRow {row_idx + 1}:")
            for col_idx, value in enumerate(row):
                if value and len(value.strip()) > 0:
                    col_name = headers[col_idx] if col_idx < len(headers) else f"Col{col_idx}"
                    print(f"  {col_name}: {value[:100]}")

        # Find pickup/dropoff columns
        print("\n[PICKUP/DROPOFF COORDINATES]:")
        for idx, col in enumerate(headers):
            col_lower = col.lower()
            if any(x in col_lower for x in ['pickup', 'dropoff', 'coordinate', 'location', 'address']):
                print(f"\n  Column {idx} ({col}):")
                for row_idx in range(1, min(4, len(values))):
                    if idx < len(values[row_idx]):
                        val = values[row_idx][idx]
                        if val:
                            print(f"    Row {row_idx + 1}: {val}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    get_buscaro_format()
