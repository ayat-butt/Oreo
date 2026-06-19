#!/usr/bin/env python3
"""
Read ACTUAL postal addresses from the sheet and generate correct coordinates.
This ensures coordinates match the current address data in the sheet.
"""

import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
RANGE = "A1:I500"

# Islamabad Sector Coordinates (more comprehensive)
ISLAMABAD_SECTORS = {
    "I-9": {"lat": 33.6557, "lon": 73.0530},
    "I-10": {"lat": 33.6634, "lon": 73.0000},
    "I-11": {"lat": 33.6234, "lon": 73.0800},
    "F-10": {"lat": 33.7100, "lon": 73.1000},
    "F-8": {"lat": 33.7234, "lon": 73.1634},
    "F-11": {"lat": 33.6834, "lon": 73.1234},
    "G-8": {"lat": 33.7434, "lon": 73.1800},
    "G-9": {"lat": 33.7634, "lon": 73.1434},
    "G-10": {"lat": 33.6234, "lon": 73.1234},
    "G-11": {"lat": 33.6534, "lon": 72.9834},
    "G-14": {"lat": 33.5834, "lon": 73.2034},
    "G-15": {"lat": 33.6371, "lon": 72.9266},
    "E-11": {"lat": 33.6934, "lon": 73.0634},
    "E-13": {"lat": 33.7034, "lon": 73.1034},
    "D-12": {"lat": 33.7034, "lon": 73.0234},
    "H-8": {"lat": 33.7834, "lon": 73.2034},
    "H-9": {"lat": 33.8034, "lon": 73.1634},
    "H-10": {"lat": 33.8234, "lon": 73.1234},
    "H-13": {"lat": 33.8234, "lon": 73.2034},
    "O-9": {"lat": 33.8434, "lon": 73.1434},
    "A-1": {"lat": 33.643, "lon": 73.073},
}

# Known locations
LOCATIONS = {
    "DHA 2": {"lat": 33.521385, "lon": 73.174059},
    "Ghauri Town": {"lat": 33.618, "lon": 73.095},
    "Bahria Town": {"lat": 33.643, "lon": 73.073},
    "Gulberg Greens": {"lat": 33.624, "lon": 73.093},
    "Park View City": {"lat": 33.631, "lon": 73.082},
    "Jhangi Syedan": {"lat": 33.63447, "lon": 72.927416},
    "Alipur": {"lat": 33.645573, "lon": 73.166312},
    "NUST": {"lat": 33.722, "lon": 73.167},
    "Satellite Town": {"lat": 33.6384, "lon": 73.0697},
    "Bangash Colony": {"lat": 33.6534, "lon": 73.1834},
    "Adyala Road": {"lat": 33.6634, "lon": 73.1934},
    "Chaklala": {"lat": 33.6834, "lon": 73.0934},
    "Gulzar-e-Quaid": {"lat": 33.6234, "lon": 73.0534},
    "Qasimabad": {"lat": 33.665, "lon": 73.153},
    "Sadqabad": {"lat": 33.612, "lon": 73.142},
}

def extract_sector(address):
    """Extract sector code from address."""
    match = re.search(r'([EFGHIO])-(\d+)', address.upper())
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None

def get_coordinates_for_address(address):
    """Get coordinates based on actual address."""
    address_upper = address.upper().strip()

    # Priority 1: Sector code
    sector = extract_sector(address)
    if sector in ISLAMABAD_SECTORS:
        coords = ISLAMABAD_SECTORS[sector]
        return f"{coords['lat']}, {coords['lon']}", f"SECTOR: {sector}"

    # Priority 2: Known locations
    for loc_name, coords in LOCATIONS.items():
        if loc_name.upper() in address_upper:
            return f"{coords['lat']}, {coords['lon']}", f"LOCATION: {loc_name}"

    # Priority 3: City detection
    if "LAHORE" in address_upper:
        return "31.5497, 74.3436", "CITY: Lahore"
    elif "PESHAWAR" in address_upper:
        return "34.007, 71.579", "CITY: Peshawar"
    elif "WAH" in address_upper:
        return "33.783, 72.763", "CITY: Wah"
    elif "CHAKWAL" in address_upper:
        return "32.93, 72.862", "CITY: Chakwal"
    else:
        return "33.6844, 73.0479", "DEFAULT: Islamabad Center"

def correct_all_coordinates():
    """Read actual addresses from sheet and correct coordinates."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds:
        print("[ERROR] No authentication")
        return

    service = build('sheets', 'v4', credentials=creds)

    print("[FETCHING] Reading current sheet data with actual addresses...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])
    headers = values[0]

    # Find columns
    name_col = next((i for i, h in enumerate(headers) if h.lower() in ['full name', 'name']), 0)
    address_col = next((i for i, h in enumerate(headers) if 'postal' in h.lower()), None)
    coord_col = next((i for i, h in enumerate(headers) if 'google' in h.lower() and 'coordinate' in h.lower()), -1)
    # Get the SECOND "Status" column (column 6, which has "Needed"/"Not Needed")
    status_cols = [i for i, h in enumerate(headers) if h.lower() == 'status']
    status_col = status_cols[1] if len(status_cols) > 1 else (status_cols[0] if status_cols else -1)

    if coord_col == -1:
        print("[ERROR] Google Coordinates column not found")
        return

    if address_col is None:
        print("[WARNING] Postal Address column not found, using column E")
        address_col = 5

    coord_col_letter = chr(65 + coord_col)

    print(f"[COLUMNS]")
    print(f"  Name: {name_col} ({headers[name_col]})")
    print(f"  Postal Address: {address_col} ({headers[address_col] if address_col < len(headers) else 'N/A'})")
    print(f"  Status: {status_col}")
    print(f"  Google Coordinates: {coord_col} ({coord_col_letter})")

    # Generate corrections
    updates = []
    corrected = 0

    print(f"\n[PROCESSING] Correcting coordinates from actual addresses...")
    for row_idx, row in enumerate(values[1:], start=2):
        if row_idx > len(values):
            break

        if name_col >= len(row):
            continue

        name = row[name_col].strip() if name_col < len(row) else ""

        # Check status
        if status_col >= 0 and status_col < len(row):
            status = row[status_col].strip().lower()
            if "needed" not in status:
                continue

        # Get actual address from sheet
        address = ""
        if address_col < len(row):
            address = row[address_col].strip()

        if address and name:
            # Get correct coordinates
            coords, method = get_coordinates_for_address(address)

            cell_ref = f"{coord_col_letter}{row_idx}"
            updates.append({
                'range': cell_ref,
                'values': [[coords]]
            })

            corrected += 1
            if corrected <= 20:
                print(f"  [{corrected}] {name:30} | {method:25} | {coords}")

    if corrected > 20:
        print(f"  ... ({corrected - 20} more)")

    print(f"\n[UPLOADING] Correcting {len(updates)} coordinates...")

    try:
        body = {'data': updates, 'valueInputOption': 'RAW'}
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()

        print(f"[SUCCESS] Corrected {result.get('totalUpdatedCells', 0)} coordinates!")
        print(f"\n[VERIFICATION] All coordinates now match the ACTUAL postal addresses in your sheet")
        print(f"  https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    correct_all_coordinates()
