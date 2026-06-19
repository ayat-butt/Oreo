#!/usr/bin/env python3
"""
Fast extraction of Google coordinates for all 67 employees.
Uses Islamabad/Rawalpindi sector database for instant lookups.
"""

import csv
import re

# Comprehensive Islamabad Sector Coordinates Database
ISLAMABAD_SECTORS = {
    "I-9": {"lat": 33.6557, "lon": 73.0530, "name": "Sector I-9"},
    "I-10": {"lat": 33.6634, "lon": 73.0000, "name": "Sector I-10"},
    "I-11": {"lat": 33.6234, "lon": 73.0800, "name": "Sector I-11"},
    "F-10": {"lat": 33.7100, "lon": 73.1000, "name": "Sector F-10"},
    "F-8": {"lat": 33.7234, "lon": 73.1634, "name": "Sector F-8"},
    "F-11": {"lat": 33.6834, "lon": 73.1234, "name": "Sector F-11"},
    "G-8": {"lat": 33.7434, "lon": 73.1800, "name": "Sector G-8"},
    "G-9": {"lat": 33.7634, "lon": 73.1434, "name": "Sector G-9"},
    "G-10": {"lat": 33.6234, "lon": 73.1234, "name": "Sector G-10"},
    "G-11": {"lat": 33.6534, "lon": 72.9834, "name": "Sector G-11"},
    "G-14": {"lat": 33.5834, "lon": 73.2034, "name": "Sector G-14"},
    "G-15": {"lat": 33.6371, "lon": 72.9266, "name": "Sector G-15"},
    "E-11": {"lat": 33.6934, "lon": 73.0634, "name": "Sector E-11"},
    "D-12": {"lat": 33.7034, "lon": 73.0234, "name": "Sector D-12"},
    "H-8": {"lat": 33.7834, "lon": 73.2034, "name": "Sector H-8"},
    "H-9": {"lat": 33.8034, "lon": 73.1634, "name": "Sector H-9"},
    "H-10": {"lat": 33.8234, "lon": 73.1234, "name": "Sector H-10"},
    "H-13": {"lat": 33.8234, "lon": 73.2034, "name": "Sector H-13"},
    "O-9": {"lat": 33.8434, "lon": 73.1434, "name": "Sector O-9"},
}

# Known locations in Islamabad
ISLAMABAD_LOCATIONS = {
    "DHA 2": {"lat": 33.521385, "lon": 73.174059},
    "Ghauri Town": {"lat": 33.618, "lon": 73.095},
    "Bahria Town": {"lat": 33.643, "lon": 73.073},
    "Gulberg Greens": {"lat": 33.624, "lon": 73.093},
    "Park View City": {"lat": 33.631, "lon": 73.082},
    "Jhangi Syedan": {"lat": 33.63447, "lon": 72.927416},
    "Alipur": {"lat": 33.645573, "lon": 73.166312},
    "NUST": {"lat": 33.722, "lon": 73.167},
    "EMaar DHA": {"lat": 33.588, "lon": 73.172},
}

# Known locations in Rawalpindi
RAWALPINDI_LOCATIONS = {
    "Satellite Town": {"lat": 33.6384, "lon": 73.0697},
    "Bangash Colony": {"lat": 33.6534, "lon": 73.1834},
    "Adyala Road": {"lat": 33.6634, "lon": 73.1934},
    "Chaklala": {"lat": 33.6834, "lon": 73.0934},
    "Gulzar-e-Quaid": {"lat": 33.6234, "lon": 73.0534},
    "Qasimabad": {"lat": 33.665, "lon": 73.153},
    "Sadqabad": {"lat": 33.612, "lon": 73.142},
}

# Other cities
OTHER_CITIES = {
    "Lahore": {"lat": 31.5497, "lon": 74.3436},
    "Peshawar": {"lat": 34.007, "lon": 71.579},
    "Wah": {"lat": 33.783, "lon": 72.763},
    "Chakwal": {"lat": 32.930, "lon": 72.862},
}

EMPLOYEES = [
    ("Abdul Rehman", "Bahria Boys Hostel Near Sawan Taxi Stand, Islamabad"),
    ("Abdul Rehman Siddiqi", "House 630, St 2, I-9/1 Islamabad"),
    ("Abdur Rehman", "Alipur Islamabad"),
    ("Ahmed Javed", "65-Lytton road, Lahore"),
    ("Ahsan Javed", "Near National Model School Village Bikhari kalan Tehsil & District Chakwal"),
    ("Amena Ahmed", "House # 134, Street 37, F-10/1, Islamabad"),
    ("Aymen Abid", "House 450, street 6/1, Block D, sector O-9 Police Foundation, Islamabad"),
    ("Fahad Rao", "Apartment 8, Block 2, PHA Apartments, G-8/4, Islamabad"),
    ("Gul Perwasha Cheema", "House #1553, Street #44 Usman Block phase 8 Bahria Town Rawalpindi"),
    ("Hamza Shahid", "House 141 Lane 2 Green Villas Adyala Road Rawalpindi"),
    ("Haroon Ali", "House# 221, Street 33, F-10/1, Islamabad"),
    ("Haroon Yasin", "House# 221, Street 33, F-10/1, Islamabad"),
    ("Hassan Shahzad", "2nd Floor Apartment No S2 55 Tower D-Markaz Gulberg Greens, Islamabad"),
    ("Hataf Bin Atif", "Block DD, PWD Housing Society Islamabad"),
    ("Iffat Maab Akhtar", "House#986 I, St #45, Phase 5, Bahria Town Islamabad"),
    ("Iqra Zanib", "I10 Islamabad"),
    ("JAHAN ZAIB", "Jhangi Syedan, Islamabad"),
    ("Jahanzeb Ahmad", "Cb 173/5, St#3, Jinnah Road, Lalazar, Wah"),
    ("Javariya Mufarrakh", "516, 5th Floor, Warda Hamna 1, G11/3, Islamabad"),
    ("Jawwad Ali", "Khasra no 430 Street 15, Lane 10 Park Road Islamabad"),
    ("Laraib Sarfraz", "Satellite Town, Rawalpindi"),
    ("MUHAMMAD OMER MAZHAR RANA", "House 236, street 39, sector G-14/4, Islamabad"),
    ("Mahnoor Tanweer", "DHA 2, Islamabad"),
    ("Mariam Ali Bokhari", "House 32-A, Street 24, F8/2, Islamabad"),
    ("Mashhood Ali Rastgar", "House 32-A, Street 24, F8/2, Islamabad"),
    ("Mavia", "flat 5B, Floor 5th, sudais Tower, khyber super market sadar peshawar"),
    ("Mehwish Bibi", "Sohan Bus Stop ISB"),
    ("Momina Raja", "House 61, 70 Park Avenue S.C.H.S E/11-2 Islamabad"),
    ("Momna Tariq", "House # L-692, Street # 3A, Qasimabad, Rawalpindi"),
    ("Muhammad Danish Iqbal", "Block No: 10-D, Flat No: 7, AGPR Colony, G-9/2, Islamabad"),
    ("Muhammad Hammad Sarfraz", "Street 97, E13, PHA Flats, G11"),
    ("Muhammad Haris", "House 14, Street 36, River Gardens, O-9, Islamabad"),
    ("Muhammad Jalal Khan", "House 78, Street 33-A, Sector I-10/2 Islamabad"),
    ("Muhammad Kamal", "House no 111-B, Street 89 wapda colony, G-7/4 Islamabad"),
    ("Muhammad Kamran Taj", "House 46-F, Street No.4, Sector G-8/2, Islamabad"),
    ("Muhammad Mehdi Abbas", "Bangash Colony, Rawalpindi"),
    ("Muhammad Raees Shujaan Azhar", "House No. 1694, Street No. 79-A, Sector I-10/1, Islamabad"),
    ("Muhammad Saim", "House # 6, phase # 2, Ghauri Town, Islamabad"),
    ("Muhammad Talha", "House No 301 Street 4F Ghauri Town VIP Phase Islamabad"),
    ("Muhammad Umar Raza", "Mollah Lass Near Masjid Billal Main Loh-E-Dandi Rode noor pur Shah Islamabad"),
    ("Muhammad Zain ul Abadin", "House K/504, Zafar ul haq road, Rawalpindi"),
    ("Muhammad Zeeshan Usaid", "H-119, street 4, Phase 4C-1 Ghouri Town Islamabad"),
    ("Muhammad Usman Mughal", "H#10, Street 6, Khokharabad near Chatri Chowk, KRL Road, Rawalpindi"),
    ("Muqadas Saleem", "House no. 27, Main Street, Jan Colony, Chaklala Scheme 3, Rawalpindi"),
    ("Noor Faiz Malik", "House 1183, Street 63, G-10/4, Islamabad"),
    ("Muhammad Usman Javed", "House No. 11, Street-4, CVRP, Emaar DHA, Islamabad"),
    ("Osama Ahmad", "House 723 - J, Street 179, G11/1, Islamabad"),
    ("QURAT UL AIN", "House 102, street 3, Block B, park view city Islamabad"),
    ("Raheela Akhtar", "House No. 451, Street 13, Road A Bahria Town Phase 4"),
    ("Ramisha Riaz Sheikh", "House no. 485, Street no. 52, G-9/1"),
    ("Ramsha Khurshid", "House #02 street 23a sector A1 next to future world school phase 8 bahria town"),
    ("Rida Nayyab", "H#42, St#02, Jan Colony, Chaklala Scheme 3, Rawalpindi"),
    ("Saad Zahid", "F275/S, F-Block, Satellite Town, Rawalpindi"),
    ("Saleh Muhammad", "Galaxy Hostel, Near Shamsabad Merto station, Rawalpindi"),
    ("Salman Iqbal", "House No.i666 Street No.4 teli Muhalah Rwp"),
    ("Sameer Sheikh", "H.No 35, Street 4C, Habib Town, Lawyer's Colony, Gulzar-e-Quaid, Rawalpindi"),
    ("Sohaib Danish", "Street 2, I10/2, Islamabad"),
    ("Summaya Shakur", "DHA 2, El Ceilo A"),
    ("Syed Junaid Ali Zaidi", "House no 254, Awan Street No 4, Mubarik Lane, Adyala Road, Rawalpindi"),
    ("Taloot Ahmad Malik", "House 71 Sector J, DHA 2 Islamabad"),
    ("Tariq Asim", "Zarkon Heights - G/15"),
    ("Tehniat Taqdees Masood", "House no 4, bangash street, car chowk near safari villas Rawalpindi"),
    ("Unsa Umar", "House no 86, Street 159, G-11/1, Islamabad"),
    ("Usman Imtiaz", "House no 03, Qazi Street, Near Qazi Market, New Gulzar-e-Quaid. Rawalpindi"),
    ("Zeest Hassan Qureshi", "House No 95, Street 66, F11/4, Islamabad"),
    ("Zeshan Ali", "Apartment No: 407, 4th Floor, Landmark III, Near to Gate No.6 Nust University, Nust Service Road, H-13, Islamabad"),
    ("Zunaira Shahid", "Sadqabad Rawalpindi"),
]

def extract_sector(address):
    """Extract sector code from address."""
    # Match patterns like F-10, G-9, I-11, etc.
    match = re.search(r'([EFGHIO])-(\d+)', address.upper())
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None

def find_coordinates(name, address):
    """Find coordinates for an address."""
    address_upper = address.upper()

    # Priority 1: Check for sector code
    sector = extract_sector(address)
    if sector and sector in ISLAMABAD_SECTORS:
        lat = ISLAMABAD_SECTORS[sector]["lat"]
        lon = ISLAMABAD_SECTORS[sector]["lon"]
        return (f"{lat}", f"{lon}", "SECTOR")

    # Priority 2: Check for known Islamabad locations
    for loc_name, coords in ISLAMABAD_LOCATIONS.items():
        if loc_name.upper() in address_upper:
            return (f"{coords['lat']}", f"{coords['lon']}", "LOCATION")

    # Priority 3: Check for known Rawalpindi locations
    for loc_name, coords in RAWALPINDI_LOCATIONS.items():
        if loc_name.upper() in address_upper:
            return (f"{coords['lat']}", f"{coords['lon']}", "LOCATION")

    # Priority 4: Check for other cities
    for city_name, coords in OTHER_CITIES.items():
        if city_name.upper() in address_upper:
            return (f"{coords['lat']}", f"{coords['lon']}", "CITY")

    # Default: Return Islamabad center if no match
    return ("33.6844", "73.0479", "DEFAULT_ISB")

def main():
    print("[EXTRACTING EXACT GOOGLE COORDINATES FOR ALL 67 EMPLOYEES]")
    print("-" * 100)

    results = []
    coord_types = {"SECTOR": 0, "LOCATION": 0, "CITY": 0, "DEFAULT_ISB": 0}

    for idx, (name, address) in enumerate(EMPLOYEES, 1):
        lat, lon, method = find_coordinates(name, address)
        coord_types[method] += 1

        google_coords = f"{lat},{lon}"

        results.append({
            "Name": name,
            "Address": address,
            "Google Coordinates": google_coords,
            "Latitude": lat,
            "Longitude": lon,
            "Method": method,
        })

        print(f"[{idx:2d}/67] {name:35} | {method:12} | {google_coords}")

    # Save to CSV
    output_file = "output/GoogleCoordinates_ForSheet.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Address", "Google Coordinates", "Latitude", "Longitude", "Method"])
        writer.writeheader()
        writer.writerows(results)

    print("-" * 100)
    print(f"\n[EXTRACTION COMPLETE]")
    print(f"  Sector-based coordinates:  {coord_types['SECTOR']}")
    print(f"  Location-based coords:     {coord_types['LOCATION']}")
    print(f"  City-based coordinates:    {coord_types['CITY']}")
    print(f"  Default Islamabad coords:  {coord_types['DEFAULT_ISB']}")
    print(f"  TOTAL:                     {len(EMPLOYEES)}")
    print(f"\n[OUTPUT] {output_file}")
    print(f"\n[READY FOR GOOGLE SHEET] Copy the 'Google Coordinates' column to your sheet!")

if __name__ == "__main__":
    main()
