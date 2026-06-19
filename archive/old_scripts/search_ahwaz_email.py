#!/usr/bin/env python3
"""Search Gmail for Ahwaz Akhtar contract email."""

from hr_assistant.config import get_google_services
from hr_assistant import gmail_service

def main():
    services = get_google_services()
    gmail = services["gmail"]

    # Search for emails mentioning Ahwaz Akhtar
    print("Searching for emails containing 'Ahwaz Akhtar'...")
    query = 'Ahwaz Akhtar'
    emails = gmail_service.search_emails(gmail, query, max_results=10)

    if not emails:
        print("No emails found containing 'Ahwaz Akhtar'.")
        return

    print(f"\nFound {len(emails)} email(s):\n")

    for i, email in enumerate(emails):
        print(f"[{i+1}] From: {email['sender']}")
        print(f"    Subject: {email['subject']}")
        print(f"    Date: {email['date'][:25]}")
        print(f"    Preview: {email['snippet'][:150]}...")
        print(f"    Email ID: {email['id']}")
        print()

if __name__ == "__main__":
    main()
