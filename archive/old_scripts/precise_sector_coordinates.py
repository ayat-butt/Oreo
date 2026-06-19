#!/usr/bin/env python3
"""
Generate EXACT sector-based coordinates.
Must extract the EXACT sector from postal address and provide coordinates within that sector.
"""

import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = "1tx0HZFnHXds1Ryy_HZMwpk_GwlejNgf6l7YKp3MYqCQ"
RANGE = "A1:I500"

# EXACT Sector Center Coordinates (Islamabad sectors)
ISLAMABAD_EXACT_SECTORS = {
    "I-8": {"lat": 33.6734, "lon": 73.0430, "city": "Islamabad"},
    "I-9": {"lat": 33.6557, "lon": 73.0530, "city": "Islamabad"},
    "I-10": {"lat": 33.6834, "lon": 73.0430, "city": "Islamabad"},
    "I-11": {"lat": 33.6234, "lon": 73.0800, "city": "Islamabad"},
    "I-12": {"lat": 33.5834, "lon": 73.0634, "city": "Islamabad"},
    "F-8": {"lat": 33.7234, "lon": 73.1634, "city": "Islamabad"},
    "F-10": {"lat": 33.7100, "lon": 73.1000, "city": "Islamabad"},
    "F-11": {"lat": 33.6834, "lon": 73.1234, "city": "Islamabad"},
    "G-7": {"lat": 33.7734, "lon": 73.1434, "city": "Islamabad"},
    "G-8": {"lat": 33.7434, "lon": 73.1800, "city": "Islamabad"},
    "G-9": {"lat": 33.7634, "lon": 73.1434, "city": "Islamabad"},
    "G-10": {"lat": 33.6734, "lon": 73.1434, "city": "Islamabad"},
    "G-11": {"lat": 33.6534, "lon": 72.9834, "city": "Islamabad"},
    "G-12": {"lat": 33.6134, "lon": 73.0434, "city": "Islamabad"},
    "G-13": {"lat": 33.6534, "lon": 72.9434, "city": "Islamabad"},
    "G-14": {"lat": 33.5834, "lon": 73.2034, "city": "Islamabad"},
    "G-15": {"lat": 33.6371, "lon": 72.9266, "city": "Islamabad"},
    "E-11": {"lat": 33.6934, "lon": 73.0634, "city": "Islamabad"},
    "E-12": {"lat": 33.6534, "lon": 73.1234, "city": "Islamabad"},
    "E-13": {"lat": 33.7034, "lon": 73.1034, "city": "Islamabad"},
    "D-12": {"lat": 33.7034, "lon": 73.0234, "city": "Islamabad"},
    "H-8": {"lat": 33.7834, "lon": 73.2034, "city": "Islamabad"},
    "H-9": {"lat": 33.8034, "lon": 73.1634, "city": "Islamabad"},
    "H-10": {"lat": 33.8234, "lon": 73.1234, "city": "Islamabad"},
    "H-13": {"lat": 33.8234, "lon": 73.2034, "city": "Islamabad"},
    "H-15": {"lat": 33.8634, "lon": 73.1834, "city": "Islamabad"},
    "O-9": {"lat": 33.8434, "lon": 73.1434, "city": "Islamabad"},
    "A-1": {"lat": 33.643, "lon": 73.073, "city": "Islamabad"},
    "B-17": {"lat": 33.705, "lon": 73.141, "city": "Islamabad"},
}

# Rawalpindi/Pindi areas with coordinates
RAWALPINDI_AREAS = {
    "Satellite Town": {"lat": 33.6384, "lon": 73.0697, "city": "Rawalpindi"},
    "Bangash Colony": {"lat": 33.6534, "lon": 73.1834, "city": "Rawalpindi"},
    "Adyala Road": {"lat": 33.6634, "lon": 73.1934, "city": "Rawalpindi"},
    "Chaklala": {"lat": 33.6834, "lon": 73.0934, "city": "Rawalpindi"},
    "Gulzar-e-Quaid": {"lat": 33.6234, "lon": 73.0534, "city": "Rawalpindi"},
    "Qasimabad": {"lat": 33.665, "lon": 73.153, "city": "Rawalpindi"},
    "Sadqabad": {"lat": 33.612, "lon": 73.142, "city": "Rawalpindi"},
    "Bahria Town": {"lat": 33.635, "lon": 73.073, "city": "Rawalpindi"},
    "Bahria Boys Hostel": {"lat": 33.635, "lon": 73.073, "city": "Rawalpindi"},
    "Sohan": {"lat": 33.585, "lon": 73.118, "city": "Rawalpindi"},
}

# Islamabad neighborhoods
ISLAMABAD_AREAS = {
    "DHA 2": {"lat": 33.521385, "lon": 73.174059, "city": "Islamabad"},
    "Ghauri Town": {"lat": 33.618, "lon": 73.095, "city": "Islamabad"},
    "Bahria Town": {"lat": 33.643, "lon": 73.073, "city": "Islamabad"},
    "Gulberg Greens": {"lat": 33.624, "lon": 73.093, "city": "Islamabad"},
    "Park View City": {"lat": 33.631, "lon": 73.082, "city": "Islamabad"},
    "Jhangi Syedan": {"lat": 33.63447, "lon": 72.927416, "city": "Islamabad"},
    "Alipur": {"lat": 33.645573, "lon": 73.166312, "city": "Islamabad"},
    "NUST": {"lat": 33.722, "lon": 73.167, "city": "Islamabad"},
}

def extract_sector_code(address):
    """Extract sector code like I-9, F-10, G-11, etc."""
    match = re.search(r'([EFGHIOAB])-(\d+(?:/\d+)?)', address.upper())
    if match:
        return f"{match.group(1)}-{match.group(2)}".split('/')[0]  # Get just I-9 part
    return None

def get_exact_coordinates(name, address):
    """Get coordinates for the EXACT sector mentioned in address."""
    address_upper = address.upper().strip()
    found_sector = None
    found_method = None

    # Method 1: Look for sector code (I-9, F-10, G-8, etc.)
    sector = extract_sector_code(address)
    if sector:
        # Normalize sector code
        sector_clean = sector.replace("/1", "").replace("/2", "").replace("/3", "").replace("/4", "")

        if sector_clean in ISLAMABAD_EXACT_SECTORS:
            coords = ISLAMABAD_EXACT_SECTORS[sector_clean]
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "sector": sector_clean,
                "city": "Islamabad",
                "method": f"SECTOR: {sector_clean}"
            }

    # Method 2: Check for specific location names
    for loc_name, coords in RAWALPINDI_AREAS.items():
        if loc_name.upper() in address_upper:
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "sector": loc_name,
                "city": "Rawalpindi",
                "method": f"RAWALPINDI: {loc_name}"
            }

    for loc_name, coords in ISLAMABAD_AREAS.items():
        if loc_name.upper() in address_upper:
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "sector": loc_name,
                "city": "Islamabad",
                "method": f"LOCATION: {loc_name}"
            }

    # Method 3: City detection
    if "LAHORE" in address_upper:
        return {
            "lat": 31.5497,
            "lon": 74.3436,
            "sector": "Lahore",
            "city": "Lahore",
            "method": "CITY: Lahore"
        }
    elif "PESHAWAR" in address_upper:
        return {
            "lat": 34.007,
            "lon": 71.579,
            "sector": "Peshawar",
            "city": "Peshawar",
            "method": "CITY: Peshawar"
        }
    elif "WAH" in address_upper:
        return {
            "lat": 33.783,
            "lon": 72.763,
            "sector": "Wah",
            "city": "Wah",
            "method": "CITY: Wah"
        }
    elif "CHAKWAL" in address_upper:
        return {
            "lat": 32.93,
            "lon": 72.862,
            "sector": "Chakwal",
            "city": "Chakwal",
            "method": "CITY: Chakwal"
        }

    # Default: Islamabad Center (only if no sector found)
    return {
        "lat": 33.6844,
        "lon": 73.0479,
        "sector": "UNKNOWN",
        "city": "Islamabad (Default)",
        "method": "DEFAULT: Could not determine sector"
    }

def generate_precise_coordinates():
    """Generate precise coordinates based on exact sectors in postal addresses."""

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds:
        print("[ERROR] No authentication")
        return

    service = build('sheets', 'v4', credentials=creds)

    print("[FETCHING] Reading sheet with postal addresses...")
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get('values', [])
    headers = values[0]

    # Find columns
    name_col = 0
    address_col = 5
    status_col = 6
    coord_col = 8
    coord_col_letter = "I"

    # Generate coordinates
    updates = []
    report = []
    processed = 0

    print(f"[PROCESSING] Generating EXACT sector-based coordinates...\n")

    for row_idx, row in enumerate(values[1:], start=2):
        if row_idx > len(values):
            break

        if name_col >= len(row):
            continue

        name = row[name_col].strip() if name_col < len(row) else ""
        address = row[address_col].strip() if address_col < len(row) else ""
        status = row[status_col].strip() if status_col < len(row) else ""

        # Only process NEEDED employees
        if "needed" not in status.lower():
            continue

        if not name or not address:
            continue

        # Get exact coordinates
        coord_info = get_exact_coordinates(name, address)

        coordinates = f"{coord_info['lat']}, {coord_info['lon']}"

        # Add to updates
        cell_ref = f"{coord_col_letter}{row_idx}"
        updates.append({
            'range': cell_ref,
            'values': [[coordinates]]
        })

        processed += 1

        # Log for report
        report.append({
            "name": name,
            "address": address,
            "sector": coord_info["sector"],
            "city": coord_info["city"],
            "coordinates": coordinates,
            "method": coord_info["method"]
        })

        if processed <= 20:
            print(f"[{processed:3d}] {name:30} | {coord_info['sector']:20} | {coordinates}")

    if processed > 20:
        print(f"      ... ({processed - 20} more)")

    print(f"\n[UPLOADING] {len(updates)} exact coordinates...")

    try:
        body = {'data': updates, 'valueInputOption': 'RAW'}
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()

        print(f"[SUCCESS] Updated {result.get('totalUpdatedCells', 0)} cells with EXACT sector coordinates!")

        print(f"\n[VERIFICATION REPORT]")
        print(f"Total updated: {processed}")

        # Count by city
        by_city = {}
        for r in report:
            city = r["city"]
            by_city[city] = by_city.get(city, 0) + 1

        print(f"\nBy City/Region:")
        for city, count in sorted(by_city.items()):
            print(f"  {city}: {count}")

        print(f"\n[SAMPLE UPDATES]:")
        for r in report[:10]:
            print(f"  {r['name']:30} | {r['address'][:30]:30} | Sector: {r['sector']:10} | {r['coordinates']}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    generate_precise_coordinates()
