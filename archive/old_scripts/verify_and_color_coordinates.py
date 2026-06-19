#!/usr/bin/env python3
"""
Cross-verify postal addresses with coordinates.
Color code: GREEN = match, RED = mismatch
"""

import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
SHEET_ID = 0
RANGE = "A1:I500"

# Sector boundaries (approximate)
SECTOR_RANGES = {
    "I-8": {"lat_min": 33.66, "lat_max": 33.68, "lon_min": 73.03, "lon_max": 73.06},
    "I-9": {"lat_min": 33.65, "lat_max": 33.67, "lon_min": 73.04, "lon_max": 73.07},
    "I-10": {"lat_min": 33.67, "lat_max": 33.70, "lon_min": 72.99, "lon_max": 73.08},
    "I-11": {"lat_min": 33.61, "lat_max": 33.64, "lon_min": 73.06, "lon_max": 73.10},
    "I-12": {"lat_min": 33.56, "lat_max": 33.60, "lon_min": 73.04, "lon_max": 73.08},
    "F-8": {"lat_min": 33.71, "lat_max": 33.74, "lon_min": 73.15, "lon_max": 73.19},
    "F-10": {"lat_min": 33.70, "lat_max": 33.73, "lon_min": 73.08, "lon_max": 73.13},
    "F-11": {"lat_min": 33.67, "lat_max": 33.70, "lon_min": 73.11, "lon_max": 73.15},
    "G-7": {"lat_min": 33.77, "lat_max": 33.80, "lon_min": 73.13, "lon_max": 73.17},
    "G-8": {"lat_min": 33.74, "lat_max": 33.77, "lon_min": 73.17, "lon_max": 73.21},
    "G-9": {"lat_min": 33.76, "lat_max": 33.79, "lon_min": 73.13, "lon_max": 73.17},
    "G-10": {"lat_min": 33.67, "lat_max": 33.70, "lon_min": 73.13, "lon_max": 73.17},
    "G-11": {"lat_min": 33.64, "lat_max": 33.67, "lon_min": 72.97, "lon_max": 73.01},
    "G-12": {"lat_min": 33.60, "lat_max": 33.63, "lon_min": 73.03, "lon_max": 73.07},
    "G-13": {"lat_min": 33.64, "lat_max": 33.67, "lon_min": 72.93, "lon_max": 72.97},
    "G-14": {"lat_min": 33.57, "lat_max": 33.60, "lon_min": 73.19, "lon_max": 73.23},
    "G-15": {"lat_min": 33.63, "lat_max": 33.65, "lon_min": 72.91, "lon_max": 72.95},
    "E-11": {"lat_min": 33.69, "lat_max": 33.72, "lon_min": 73.05, "lon_max": 73.09},
    "E-12": {"lat_min": 33.65, "lat_max": 33.68, "lon_min": 73.11, "lon_max": 73.15},
    "E-13": {"lat_min": 33.70, "lat_max": 33.73, "lon_min": 73.09, "lon_max": 73.13},
    "D-12": {"lat_min": 33.70, "lat_max": 33.73, "lon_min": 73.01, "lon_max": 73.05},
    "H-8": {"lat_min": 33.78, "lat_max": 33.81, "lon_min": 73.19, "lon_max": 73.23},
    "H-9": {"lat_min": 33.80, "lat_max": 33.83, "lon_min": 73.15, "lon_max": 73.19},
    "H-10": {"lat_min": 33.82, "lat_max": 33.85, "lon_min": 73.11, "lon_max": 73.15},
    "H-13": {"lat_min": 33.82, "lat_max": 33.85, "lon_min": 73.19, "lon_max": 73.23},
    "O-9": {"lat_min": 33.84, "lat_max": 33.87, "lon_min": 73.13, "lon_max": 73.17},
}

# Location ranges
LOCATION_RANGES = {
    "Bahria Town": {"lat_min": 33.62, "lat_max": 33.66, "lon_min": 73.06, "lon_max": 73.10},
    "DHA 2": {"lat_min": 33.50, "lat_max": 33.54, "lon_min": 73.16, "lon_max": 73.20},
    "Ghauri Town": {"lat_min": 33.61, "lat_max": 33.63, "lon_min": 73.08, "lon_max": 73.11},
    "Alipur": {"lat_min": 33.64, "lat_max": 33.67, "lon_min": 73.15, "lon_max": 73.19},
    "Satellite Town": {"lat_min": 33.63, "lat_max": 33.65, "lon_min": 73.06, "lon_max": 73.08},
    "Bangash Colony": {"lat_min": 33.65, "lat_max": 33.67, "lon_min": 73.17, "lon_max": 73.20},
    "Adyala Road": {"lat_min": 33.66, "lat_max": 33.68, "lon_min": 73.18, "lon_max": 73.21},
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

def coord_in_sector(lat, lon, sector):
    """Check if coordinates fall within sector range."""
    if sector not in SECTOR_RANGES:
        return False

    s = SECTOR_RANGES[sector]
    return s["lat_min"] <= lat <= s["lat_max"] and s["lon_min"] <= lon <= s["lon_max"]

def coord_in_location(lat, lon, location):
    """Check if coordinates fall within location range."""
    if location not in LOCATION_RANGES:
        return False

    loc = LOCATION_RANGES[location]
    return loc["lat_min"] <= lat <= loc["lat_max"] and loc["lon_min"] <= lon <= loc["lon_max"]

def verify_and_color():
    """Verify coordinates and apply formatting."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds:
        print("[ERROR] No authentication")
        return

    service = build('sheets', 'v4', credentials=creds)

    print("[FETCHING] Reading sheet data...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])
    headers = values[0]

    # Column indices
    name_col = 0
    address_col = 5
    status_col = 6
    coord_col = 8

    # Verification results
    matches = []
    mismatches = []
    unknowns = []

    print("[VERIFYING] Cross-checking postal addresses with coordinates...\n")

    for row_idx, row in enumerate(values[1:], start=2):
        if row_idx > len(values):
            break

        if name_col >= len(row):
            continue

        name = row[name_col].strip() if name_col < len(row) else ""
        address = row[address_col].strip() if address_col < len(row) else ""
        status = row[status_col].strip() if status_col < len(row) else ""
        coord_str = row[coord_col].strip() if coord_col < len(row) else ""

        # Only process NEEDED employees
        if "needed" not in status.lower():
            continue

        if not name or not address or not coord_str:
            continue

        # Parse coordinates
        try:
            parts = coord_str.split(',')
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
        except:
            unknowns.append({"row": row_idx, "name": name, "reason": "Invalid coordinate format"})
            continue

        # Extract sector/location from address
        sector = extract_sector(address)
        location = extract_location(address)

        # Check if coordinates match
        is_match = False
        match_type = None

        if sector:
            if coord_in_sector(lat, lon, sector):
                is_match = True
                match_type = f"SECTOR: {sector}"
        elif location:
            if coord_in_location(lat, lon, location):
                is_match = True
                match_type = f"LOCATION: {location}"
        else:
            # Can't determine - mark as unknown
            unknowns.append({"row": row_idx, "name": name, "address": address, "reason": "No clear sector/location in address"})
            continue

        if is_match:
            matches.append({"row": row_idx, "name": name, "address": address, "match": match_type})
        else:
            mismatches.append({"row": row_idx, "name": name, "address": address, "sector": sector or location, "coords": coord_str})

    print(f"[RESULTS]")
    print(f"  MATCH (GREEN): {len(matches)}")
    print(f"  MISMATCH (RED): {len(mismatches)}")
    print(f"  UNKNOWN: {len(unknowns)}\n")

    # Show samples
    if matches:
        print(f"[SAMPLE MATCHES - GREEN]:")
        for m in matches[:5]:
            print(f"  [OK] {m['name']:30} | {m['match']}")

    if mismatches:
        print(f"\n[SAMPLE MISMATCHES - RED]:")
        for m in mismatches[:5]:
            print(f"  [XX] {m['name']:30} | Address says: {m['sector']:15} | Coords: {m['coords']}")

    # Prepare formatting
    print(f"\n[FORMATTING] Applying colors to sheet...")

    requests = []

    # GREEN formatting for matches
    if matches:
        match_ranges = [f"I{m['row']}" for m in matches]
        for match_range in match_ranges:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": SHEET_ID,
                        "rangeA1": match_range,
                        "endRowIndex": int(match_range[1:]) - 1 + 1,
                        "startRowIndex": int(match_range[1:]) - 1,
                        "startColumnIndex": 8,
                        "endColumnIndex": 9
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.0,
                                "green": 1.0,
                                "blue": 0.0,
                                "alpha": 0.3
                            }
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

    # RED formatting for mismatches
    if mismatches:
        mismatch_ranges = [f"I{m['row']}" for m in mismatches]
        for mismatch_range in mismatch_ranges:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": SHEET_ID,
                        "rangeA1": mismatch_range,
                        "endRowIndex": int(mismatch_range[1:]) - 1 + 1,
                        "startRowIndex": int(mismatch_range[1:]) - 1,
                        "startColumnIndex": 8,
                        "endColumnIndex": 9
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 1.0,
                                "green": 0.0,
                                "blue": 0.0,
                                "alpha": 0.3
                            }
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

    # Apply formatting
    if requests:
        try:
            batch_request = {"requests": requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=batch_request
            ).execute()

            print(f"[SUCCESS] Applied colors!")
            print(f"  GREEN (Matches): {len(matches)} cells")
            print(f"  RED (Mismatches): {len(mismatches)} cells")

        except Exception as e:
            print(f"[ERROR] {e}")

    print(f"\n[VERIFICATION COMPLETE]")
    print(f"Check your sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")
    print(f"\nLegend:")
    print(f"  🟢 GREEN = Postal address sector MATCHES coordinate location")
    print(f"  🔴 RED = Postal address sector DOES NOT MATCH coordinate location")

    # Show mismatches that need fixing
    if mismatches:
        print(f"\n[NEEDS FIXING - {len(mismatches)} MISMATCHES]:")
        for m in mismatches[:15]:
            print(f"  [XX] {m['name']:30} | Address: {m['sector']:15} | Current: {m['coords']}")

if __name__ == "__main__":
    verify_and_color()
