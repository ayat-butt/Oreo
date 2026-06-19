#!/usr/bin/env python3
"""Final email preview with CC recipients for Muhammad Ahmed."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CANDIDATE = {
    "name": "Muhammad Ahmed",
    "first_name": "Muhammad",
    "position": "AI Engineer Intern (Fellowship)",
    "start_date": "Monday, 1st of June 2026",
    "company": "Taleemabad, powered by Orenda",
    "compensation": "40",
    "employment_type": "full-time, fellowship-based",
    "email": "[PENDING]",
}

CC_RECIPIENTS = [
    "hr@taleemabad.com",
    "hiring@taleemabad.com",
    "accounts.query@taleemabad.com",
    "mashhood.ali.rastgar@taleemabad.com",
]

ONBOARDING_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSf70SM4jlx4muDMLlN1ZMqHqVEQjJQgCBga-oRM-M1OZXCePw/viewform?usp=sharing&ouid=108638480093303713396&urp=gmail_link"
WHATSAPP_LINK = "https://chat.whatsapp.com/HglkfuENmLqEbaq8N5jSVq"

def main():
    print("=" * 120)
    print("FINAL EMAIL PREVIEW - MUHAMMAD AHMED (WITH CC)")
    print("=" * 120)

    print(f"\nFrom:    Ayat Butt <ayat@niete.edu.pk>")
    print(f"To:      Muhammad Ahmed <{CANDIDATE['email']}>")
    print(f"\nCC Recipients:")
    for i, cc in enumerate(CC_RECIPIENTS, 1):
        print(f"  {i}. {cc}")

    print(f"\nSubject: Welcome to Taleemabad - {CANDIDATE['position']}")
    print(f"\nAttachments:")
    print(f"  - Muhammad Ahmed - Contract.pdf")
    print(f"  - Muhammad Ahmed - NDA.pdf")

    print("\n" + "-" * 120)
    print("EMAIL BODY:")
    print("-" * 120 + "\n")

    email_body = (
        f"Dear {CANDIDATE['first_name']},\n\n"
        f"I hope you read this in good health and high spirits.\n\n"
        f"We are pleased to announce that you have been selected for the position of {CANDIDATE['position']} at {CANDIDATE['company']}, starting {CANDIDATE['start_date']}. Your monthly compensation for this {CANDIDATE['employment_type']} role is PKR {CANDIDATE['compensation']},000, inclusive of taxes.\n\n"
        f"Please find the Contract and Non-Disclosure Agreement (NDA) attached to this email.\n\n"
        f"Additionally, please take note of the essential logistical requirements outlined below:\n\n"
        f"Complete the form linked here with your information for record-keeping purposes and upload your educational documents, signed contracts, a signed NDA, and an experience letter: {ONBOARDING_FORM}\n\n"
        f"Provide your bank name, account title, and IBAN number, matching the details on your cheque book. Upon the submission of all required documents, we will proceed to set up your teams and email ID.\n\n"
        f"Join the Orenda | Taleemabad WhatsApp Group via the following link: {WHATSAPP_LINK}\n\n"
        f"Once you are officially registered in the company records, you will receive an HR portal account activation email.\n\n"
        f"Welcome to the team once again!\n\n"
        f"Should you have any queries or concerns, please feel free to reach out to the HR team.\n\n"
        f"Warm regards,\n"
        f"Oreo\n"
        f"Ayat's Personal AI Assistant -- Taleemabad"
    )

    print(email_body)

    print("\n" + "-" * 120)
    print("\n" + "=" * 120)
    print("EMAIL READY TO SEND")
    print("=" * 120)
    print(f"\nSummary:")
    print(f"  ✓ To: Muhammad Ahmed (email address pending)")
    print(f"  ✓ CC: {len(CC_RECIPIENTS)} recipients")
    print(f"  ✓ Subject: Welcome to Taleemabad - {CANDIDATE['position']}")
    print(f"  ✓ Attachments: Contract PDF + NDA PDF")
    print(f"  ✓ Form Link: Included")
    print(f"  ✓ WhatsApp Link: Included")
    print("\n" + "=" * 120)

if __name__ == "__main__":
    main()
