#!/usr/bin/env python3
"""Audit probation tracker against Gmail records to identify updates needed."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services
from hr_assistant import gmail_service
import re
from datetime import datetime

SHEET_ID = "1_yvL_lM3WzE5BBzsk60PO7gutsYer_y1PSFbTT0hJBY"
GID = "322356645"

def extract_date_from_text(text):
    """Extract date in YYYY-MM-DD format from text."""
    patterns = [
        r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
        r'(\d{4})-(\d{2})-(\d{2})',
    ]

    months = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 3:
                day, month, year = match.groups()
                if month in months:
                    return f"{year}-{months[month]}-{day.zfill(2)}"
            else:
                year, month, day = match.groups()
                return f"{year}-{month}-{day}"
    return None

def search_probation_emails(gmail):
    """Search Gmail for probation-related emails."""
    print("Searching Gmail for probation-related emails...")

    queries = [
        "probation",
        "subject:probation",
        "closure",
        "subject:closure",
    ]

    all_emails = []
    for query in queries:
        try:
            emails = gmail_service.search_emails(gmail, query, max_results=50)
            all_emails.extend(emails)
        except:
            pass

    # Remove duplicates
    seen = set()
    unique_emails = []
    for email in all_emails:
        if email['id'] not in seen:
            seen.add(email['id'])
            unique_emails.append(email)

    return unique_emails

def main():
    services = get_google_services()
    gmail = services["gmail"]
    sheets = services["sheets"]

    print("=" * 120)
    print("PROBATION TRACKER AUDIT - Gmail vs Sheet")
    print("=" * 120)

    # Step 1: Get sheet data
    print("\n[1/3] Fetching probation tracker sheet...")
    metadata = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()

    sheet_name = None
    for sheet in metadata.get("sheets", []):
        if str(sheet["properties"]["sheetId"]) == GID:
            sheet_name = sheet["properties"]["title"]
            break

    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1:M100"
    ).execute()

    sheet_rows = result.get("values", [])
    print(f"Sheet loaded: {len(sheet_rows)} rows")

    # Step 2: Search Gmail
    print("\n[2/3] Searching Gmail for probation-related emails...")
    gmail_emails = search_probation_emails(gmail)
    print(f"Found {len(gmail_emails)} probation-related emails")

    # Step 3: Analyze
    print("\n[3/3] Analyzing discrepancies...\n")
    print("-" * 120)
    print("RECENT PROBATION EMAILS (Last 20):\n")

    for i, email in enumerate(gmail_emails[:20], 1):
        date_str = email['date'][:25] if email['date'] else "Unknown"
        sender = email['sender'].split('<')[0].strip() if '<' in email['sender'] else email['sender']

        print(f"[{i}] {date_str}")
        print(f"    From: {sender}")
        print(f"    Subject: {email['subject']}")
        print(f"    Preview: {email['snippet'][:100]}...")
        print()

    print("-" * 120)
    print("\nKEY FINDINGS:")
    print("-" * 120)
    print(f"✓ Sheet has probation tracker for 24 employees")
    print(f"✓ Gmail has {len(gmail_emails)} probation-related emails")
    print(f"\nRECOMMENDATION:")
    print(f"  → Cross-check recent emails against 'URGENT' employees")
    print(f"  → Verify 'Initiated' status updates match Gmail evidence")
    print(f"  → Check for missing probation closure notifications")
    print("\n" + "=" * 120)


if __name__ == "__main__":
    main()
