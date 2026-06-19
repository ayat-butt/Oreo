#!/usr/bin/env python3
"""Update the welcome email draft with the latest contract PDF."""

from hr_assistant.config import get_google_services
from hr_assistant.email_service import draft_welcome_email

EMPLOYEE = {
    "name": "Ahwaz Akhtar",
    "email": "ahwaz.akhtar@taleemabad.com",
    "designation": "M&E Lead",
    "joining_date": "01 April 2026",
    "salary": "600,000",
}

# Contract and NDA doc IDs from the generated documents
CONTRACT_ID = "1sXoOGFEuFuZoJndjppcTZR_IoGz3_YkhJ5oZLlMyIAY"
NDA_ID = "1KbSJVbM9iqkeuKRkjBAZmkYzp-29ygcWaymPYS3beoA"

def main():
    print("Connecting to Google services...")
    services = get_google_services()
    drive = services["drive"]
    gmail = services["gmail"]

    print("Regenerating welcome email draft with updated contract PDF...")
    email_result = draft_welcome_email(drive, gmail, EMPLOYEE, CONTRACT_ID, NDA_ID)

    print("\n" + "=" * 70)
    print("EMAIL DRAFT UPDATED")
    print("=" * 70)
    print(f"Subject: {email_result['subject']}")
    print(f"To:      {email_result['to']}")
    print(f"Status:  [DRAFT] Saved as draft in Gmail Drafts (with updated PDFs)")
    print("=" * 70)

if __name__ == "__main__":
    main()
