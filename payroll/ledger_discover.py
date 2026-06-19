#!/usr/bin/env python3
"""
Discovery: list tabs in each payroll source sheet and locate Ayesha Jamshaid.
Read-only. Uses token.json (Sheets API v4).
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

SHEETS = [
    ("May 2024",            "1QfbGtkAuXiq3tqi8koULWED2HtOOpPzbXRoMgwlFk0U"),
    ("Jun2024-Jun2025",     "1ij5ogY-c1crNUbU2UD9KhIN6g1sJspXfDdsCz9fH8QE"),
    ("July 2025",           "1j9IYtxj38mUYPT8kOGOhuyOm7wtbiccaCjxJPTvlM24"),
    ("August 2025",         "1FCiMTGim6EqWJRL7UVA3V31bH8KvICVs7a895pjoIuE"),
    ("September 2025",      "1sLo1cv5tWqoj1Shtyp2eZjSW6UEz_z__VU8CnFDfW-A"),
    ("October 2025",        "1nCuye_IqKEipyKNWvAz9pJ3LLwEpnR2z6raoPVfmGRY"),
    ("November 2025",       "1NHnjvsJc-hk9l7qQvOTQr3znKFPzjc9mEBbtKWmJjjA"),
    ("December 2025",       "1FprPYHx-S_RaV-C5HGGENg3BVeWzhmn3eUx1Ofuk7gk"),
]

NEEDLE = "ayesha"

def main():
    s = svc()
    for label, sid in SHEETS:
        print("\n" + "="*70)
        print(f"SHEET: {label}  ({sid})")
        print("="*70)
        try:
            meta = s.spreadsheets().get(spreadsheetId=sid).execute()
        except Exception as e:
            print(f"  ERROR opening: {e}")
            continue
        tabs = [sh['properties']['title'] for sh in meta.get('sheets', [])]
        print(f"  Tabs ({len(tabs)}): {tabs}")
        for tab in tabs:
            try:
                res = s.spreadsheets().values().get(
                    spreadsheetId=sid, range=f"'{tab}'!A1:AZ2000"
                ).execute()
            except Exception as e:
                print(f"    [{tab}] read error: {e}")
                continue
            rows = res.get('values', [])
            for ri, row in enumerate(rows):
                joined = " | ".join(str(c) for c in row).lower()
                if NEEDLE in joined:
                    print(f"    >> MATCH in tab '{tab}' row {ri+1}: {row}")

if __name__ == '__main__':
    main()
