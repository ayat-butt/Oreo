#!/usr/bin/env python3
"""
Update coordinates for employees marked "NEEDED" in the sheet.
Matches by name and finds the NEEDED status.
"""

import csv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
RANGE = "A1:Z500"

def load_all_coordinates():
    """Load all coordinates we have."""
    coords = {}
    with open('output/GoogleCoordinates_ForSheet.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Name'].strip()
            parts = row['Google Coordinates'].split(',')
            if len(parts) >= 2:
                lat = parts[0].strip()
                lon = parts[1].strip()
                coords[name] = f"{lat}, {lon}"
    return coords

def update_needed_employees():
    """Update only employees marked NEEDED."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds:
        print("[ERROR] No authentication")
        return

    service = build('sheets', 'v4', credentials=creds)

    # Load coordinates
    print("[LOADING] Coordinates...")
    all_coords = load_all_coordinates()

    # Get sheet data
    print("[FETCHING] Full sheet data...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])
    headers = values[0]

    print(f"[INFO] Found {len(headers)} columns")
    print(f"[COLUMNS]: {headers}")

    # Find relevant columns
    name_col_idx = -1
    status_col_idx = -1
    coord_col_idx = -1

    for idx, header in enumerate(headers):
        h = header.lower().strip()
        if h in ['full name', 'name']:
            name_col_idx = idx
        elif 'status' in h and 'address' not in h:
            status_col_idx = idx
        elif 'google' in h and 'coordinate' in h:
            coord_col_idx = idx

    print(f"[COLUMNS FOUND]")
    print(f"  Name: {name_col_idx} ({headers[name_col_idx] if name_col_idx >= 0 else 'NOT FOUND'})")
    print(f"  Status: {status_col_idx} ({headers[status_col_idx] if status_col_idx >= 0 else 'NOT FOUND'})")
    print(f"  Google Coordinates: {coord_col_idx} ({headers[coord_col_idx] if coord_col_idx >= 0 else 'NOT FOUND'})")

    if coord_col_idx == -1:
        print("[ERROR] Google Coordinates column not found")
        return

    coord_col_letter = chr(65 + coord_col_idx)

    # Process rows
    updates = []
    needed_count = 0
    updated_count = 0

    print(f"\n[PROCESSING] Finding NEEDED employees...")
    for row_idx, row in enumerate(values[1:], start=2):
        if row_idx > len(values):
            break

        # Get name
        if name_col_idx >= len(row):
            continue
        name = row[name_col_idx].strip() if name_col_idx < len(row) else ""

        # Get status
        status = ""
        if status_col_idx >= 0 and status_col_idx < len(row):
            status = row[status_col_idx].strip()

        # Check if NEEDED
        if "needed" in status.lower():
            needed_count += 1

            # Try to find coordinates
            if name in all_coords:
                coord = all_coords[name]
                cell_ref = f"{coord_col_letter}{row_idx}"
                updates.append({
                    'range': cell_ref,
                    'values': [[coord]]
                })
                updated_count += 1

                if updated_count <= 15:
                    print(f"  [{updated_count}] {name:35} (Status: {status}) -> {coord}")

    if updated_count > 15:
        print(f"  ... ({updated_count - 15} more)")

    print(f"\n[SUMMARY]")
    print(f"  Total NEEDED in sheet: {needed_count}")
    print(f"  Coordinates found: {updated_count}")
    print(f"  Updates to apply: {len(updates)}")

    # Upload
    if updates:
        print(f"\n[UPLOADING] Updating {len(updates)} cells...")
        try:
            body = {'data': updates, 'valueInputOption': 'RAW'}
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()

            print(f"[SUCCESS] Updated {result.get('totalUpdatedCells', 0)} cells!")
            print(f"\n[VERIFICATION] Check your sheet:")
            print(f"  https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")

        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    update_needed_employees()
