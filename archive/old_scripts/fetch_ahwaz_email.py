#!/usr/bin/env python3
"""Fetch full email content for Ahwaz Akhtar contract."""

from hr_assistant.config import get_google_services
from hr_assistant import gmail_service

def main():
    services = get_google_services()
    gmail = services["gmail"]

    # Fetch the specific email with ID from the search
    email_id = "19d75d70810fdbae"  # From [1] in search results

    msg = gmail.users().messages().get(
        userId="me",
        id=email_id,
        format="full",
    ).execute()

    email = gmail_service._parse_email(msg)

    print("=" * 70)
    print("CONTRACT REQUEST EMAIL - AHWAZ AKHTAR")
    print("=" * 70)
    print(f"From:    {email['sender']}")
    print(f"To:      {email['to']}")
    print(f"Subject: {email['subject']}")
    print(f"Date:    {email['date']}")
    print("-" * 70)
    print("\nEMAIL BODY:")
    print("-" * 70)
    print(email['body'])
    print("-" * 70)

if __name__ == "__main__":
    main()
