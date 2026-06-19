#!/usr/bin/env python3
"""
Dump header rows + Ayesha Jamshaid's row (indexed per cell) for each relevant tab,
so columns can be mapped precisely. Read-only. Locks onto CNIC 37405-5447991-6.
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

def svc():
    with open('token.json') as f:
        t = json.load(f)
    c = Credentials.from_authorized_user_info(t)
    if c.expired:
        c.refresh(Request())
    return build('sheets', 'v4', credentials=c)

CNIC = "37405-5447991-6"
TARGET = "ayesha jamshaid"

# (label, spreadsheet_id, tab, header_rows_to_show)
TARGETS = [
    ("May 2024",       "1QfbGtkAuXiq3tqi8koULWED2HtOOpPzbXRoMgwlFk0U", "MonthlyPayroll_2023_12", 1),
    ("June 2024",      "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "June 2024", 11),
    ("July 2024",      "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "July 2024", 10),
    ("August 2024",    "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "August 2024", 10),
    ("September 2024", "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "September 2024", 6),
    ("October 2024",   "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "October 2024", 6),
    ("November 2024",  "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "November 2024", 3),
    ("December 2024",  "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "December 2024", 3),
    ("January 2025",   "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "January 2025", 4),
    ("February 2025",  "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "February 2025", 4),
    ("March 2025",     "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "March 2025", 3),
    ("April 2025",     "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "April 2025", 2),
    ("May 2025",       "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE", "May 2025", 2),
    ("July 2025",      "1j9IYtxj38mUYPT8kOGOhuyOm7wtbiccaCjxJPTvlM24", "OWT", 5),
    ("August 2025",    "1FCiMTGim6EqWJRL7UVA3V31bH8KvICVs7a895pjoIuE", "OWT", 5),
    ("September 2025", "1sLo1cv5tWqoj1Shtyp2eZjSW6UEz_z__VU8CnFDfW-A", "OWT", 5),
    ("October 2025",   "1nCuye_IqKEipyKNWvAz9pJ3LLwEpnR2z6raoPVfmGRY", "OWT", 5),
    ("November 2025",  "1NHnjvsJc-hk9l7qQvOTQr3znKFPzjc9mEBbtKWmJjjA", "OWT", 5),
    ("December 2025",  "1FprPYHx-S_RaV-C5HGGENg3BVeWzhmn3eUx1Ofuk7gk", "OWT", 5),
]

def idx(row):
    return " ".join(f"[{i}]{repr(v)}" for i, v in enumerate(row))

def main():
    s = svc()
    for label, sid, tab, hrows in TARGETS:
        print("\n" + "="*80)
        print(f"### {label}  | tab='{tab}'")
        print("="*80)
        try:
            res = s.spreadsheets().values().get(
                spreadsheetId=sid, range=f"'{tab}'!A1:BA300"
            ).execute()
        except Exception as e:
            print(f"  read error: {e}")
            continue
        rows = res.get('values', [])
        print(f"-- header rows (first {hrows}) --")
        for ri in range(min(hrows, len(rows))):
            print(f"  R{ri+1}: {idx(rows[ri])}")
        # find Ayesha Jamshaid row (prefer CNIC, else name)
        found = None
        for ri, row in enumerate(rows):
            joined = " | ".join(str(c) for c in row)
            if CNIC in joined or TARGET in joined.lower() and "jamshaid" in joined.lower():
                if "jamshaid" in joined.lower():
                    found = (ri, row)
                    break
        if found:
            ri, row = found
            print(f"-- AYESHA row R{ri+1} --")
            print(f"  {idx(row)}")
        else:
            print("  !! Ayesha Jamshaid NOT found in this tab")

if __name__ == '__main__':
    main()
