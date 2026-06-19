#!/usr/bin/env python3
"""
Apply color formatting to coordinates.
Green = match, Red = mismatch
"""

import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
SHEET_ID = 361249755  # Members sheet
RANGE = "A1:I500"

# Sector ranges
SECTOR_RANGES = {
    "I-8": {"lat_min": 33.66, "lat_max": 33.68, "lon_min": 73.03, "lon_max": 73.06},
    "I-9": {"lat_min": 33.65, "lat_max": 33.67, "lon_min": 73.04, "lon_max": 73.07},
    "I-10": {"lat_min": 33.67, "lat_max": 33.70, "lon_min": 72.99, "lon_max": 73.08},
    "I-11": {"lat_min": 33.61, "lat_max": 33.64, "lon_min": 73.06, "lon_max": 73.10},
    "F-10": {"lat_min": 33.70, "lat_max": 33.73, "lon_min": 73.08, "lon_max": 73.13},
    "G-8": {"lat_min": 33.74, "lat_max": 33.77, "lon_min": 73.17, "lon_max": 73.21},
    "G-11": {"lat_min": 33.64, "lat_max": 33.67, "lon_min": 72.97, "lon_max": 73.01},
    "E-11": {"lat_min": 33.69, "lat_max": 33.72, "lon_min": 73.05, "lon_max": 73.09},
    "H-13": {"lat_min": 33.82, "lat_max": 33.85, "lon_min": 73.19, "lon_max": 73.23},
    "O-9": {"lat_min": 33.84, "lat_max": 33.87, "lon_min": 73.13, "lon_max": 73.17},
}

LOCATION_RANGES = {
    "Bahria Town": {"lat_min": 33.62, "lat_max": 33.66, "lon_min": 73.06, "lon_max": 73.10},
    "DHA 2": {"lat_min": 33.50, "lat_max": 33.54, "lon_min": 73.16, "lon_max": 73.20},
    "Alipur": {"lat_min": 33.64, "lat_max": 33.67, "lon_min": 73.15, "lon_max": 73.19},
    "Satellite Town": {"lat_min": 33.63, "lat_max": 33.65, "lon_min": 73.06, "lon_max": 73.08},
}

def extract_sector(address):
    """Extract sector code from address."""
    match = re.search(r'([EFGHIO])-(\d+)', address.upper())
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None

def extract_location(address):
    """Extract location name from address."""
    address_upper = address.upper()
    for loc in LOCATION_RANGES.keys():
        if loc.upper() in address_upper:
            return loc
    return None

def coord_in_range(lat, lon, lat_min, lat_max, lon_min, lon_max):
    """Check if coordinates are within range."""
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

def verify_coordinates():
    """Verify and color code coordinates."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    service = build('sheets', 'v4', credentials=creds)

    print("[FETCHING] Reading sheet data...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])

    # Verify
    match_rows = []
    mismatch_rows = []

    print("[VERIFYING] Cross-checking addresses with coordinates...\n")

    for row_idx, row in enumerate(values[1:], start=2):
        if not row or len(row) < 9:
            continue

        name = row[0].strip() if len(row) > 0 else ""
        address = row[5].strip() if len(row) > 5 else ""
        status = row[6].strip() if len(row) > 6 else ""
        coord_str = row[8].strip() if len(row) > 8 else ""

        if "needed" not in status.lower() or not coord_str:
            continue

        try:
            parts = coord_str.split(',')
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
        except:
            continue

        sector = extract_sector(address)
        location = extract_location(address)

        is_match = False

        if sector and sector in SECTOR_RANGES:
            s = SECTOR_RANGES[sector]
            if coord_in_range(lat, lon, s["lat_min"], s["lat_max"], s["lon_min"], s["lon_max"]):
                is_match = True
                match_type = f"{sector}"

        if not is_match and location and location in LOCATION_RANGES:
            loc = LOCATION_RANGES[location]
            if coord_in_range(lat, lon, loc["lat_min"], loc["lat_max"], loc["lon_min"], loc["lon_max"]):
                is_match = True
                match_type = location

        if is_match:
            match_rows.append(row_idx)
        else:
            mismatch_rows.append(row_idx)

    print(f"[RESULTS]")
    print(f"  MATCH (GREEN): {len(match_rows)}")
    print(f"  MISMATCH (RED): {len(mismatch_rows)}\n")

    # Apply colors using simple format update
    print("[APPLYING COLORS] Updating cells...")

    updates = []

    # Green for matches
    for row in match_rows:
        updates.append({
            "range": f"I{row}",
            "values": [[]]  # Keep value, just format it
        })

    # Red for mismatches
    for row in mismatch_rows:
        updates.append({
            "range": f"I{row}",
            "values": [[]]
        })

    # Use format API instead
    format_requests = []

    # Green formatting
    for row in match_rows:
        format_requests.append({
            "updateCells": {
                "rows": [{
                    "values": [{
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0,
                                "green": 1,
                                "blue": 0,
                                "alpha": 0.3
                            }
                        }
                    }]
                }],
                "range": {
                    "sheetId": SHEET_ID,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": 8,
                    "endColumnIndex": 9
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })

    # Red formatting
    for row in mismatch_rows:
        format_requests.append({
            "updateCells": {
                "rows": [{
                    "values": [{
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 1,
                                "green": 0,
                                "blue": 0,
                                "alpha": 0.3
                            }
                        }
                    }]
                }],
                "range": {
                    "sheetId": SHEET_ID,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": 8,
                    "endColumnIndex": 9
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })

    # Apply formatting
    if format_requests:
        try:
            batch_update_request = {
                "requests": format_requests
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=batch_update_request
            ).execute()

            print(f"[SUCCESS] Applied colors!")
            print(f"  GREEN: {len(match_rows)} cells")
            print(f"  RED: {len(mismatch_rows)} cells")

        except Exception as e:
            print(f"[ERROR] {e}")

    print(f"\n[DONE] Check your Google Sheet:")
    print(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")

if __name__ == "__main__":
    verify_coordinates()
