#!/usr/bin/env python3
"""Preview the email that will be sent with CC list."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

EMPLOYEE = {
    "first_name": "Ahwaz",
    "name": "Ahwaz Akhtar",
    "email": "ahwaz.akhtar@taleemabad.com",
    "designation": "M&E Lead",
    "joining_date": "01 April 2026",
    "salary": "600,000",
    "new_employment": "Full-time, Permanent",
}

CC_LIST = [
    "sabeena.abbasi@taleemabad.com",
    "hiring@taleemabad.com",
    "hr@taleemabad.com",
    "accounts.query@taleemabad.com",
]

def build_role_change_email(emp: dict) -> str:
    """Build HTML body for employment term change email."""
    first_name = emp["first_name"]
    designation = emp["designation"]
    joining_date = emp["joining_date"]
    salary = emp["salary"]
    new_employment = emp["new_employment"]

    return (
        f'Hi {first_name},\n\n'
        f'We are delighted to confirm the updates to your employment terms, effective {joining_date}. '
        f'Your status will transition from part-time (75% capacity) to {new_employment}, in your role as {designation}, '
        f'with a revised monthly compensation of PKR {salary} (gross).\n\n'
        f'Your continued dedication and excellent contributions have made you a valuable member of our team, '
        f'and we look forward to your continued growth and impact in this capacity.\n\n'
        f'Please find the updated Contract and Non-Disclosure Agreement (NDA) attached to this email. '
        f'Kindly review, sign, and return both documents as attachments in your reply.\n\n'
        f'We already have your personal and employment details on file. '
        f'However, if there are any changes or updates needed to your records, please let us know in this email thread and we will ensure everything is updated accordingly.\n\n'
        f'Should you have any questions or concerns regarding your updated employment terms or compensation, '
        f'please feel free to reach out to the HR team.\n\n'
        f'Warm regards,\n'
        f'Oreo\n'
        f'Ayat\'s Personal AI Assistant -- Taleemabad'
    )

print("=" * 80)
print("FINAL EMAIL PREVIEW - READY TO SEND")
print("=" * 80)
print(f"\nFrom:    Ayat Butt <ayat@niete.edu.pk>")
print(f"To:      {EMPLOYEE['name']} <{EMPLOYEE['email']}>")
print(f"\nCC Recipients:")
for i, cc in enumerate(CC_LIST, 1):
    print(f"  {i}. {cc}")
print(f"\nSubject: Confirmation of Updated Employment Terms - {EMPLOYEE['designation']}")
print(f"\nAttachments:")
print(f"  - {EMPLOYEE['name']} - Contract.pdf")
print(f"  - {EMPLOYEE['name']} - NDA.pdf")
print("\n" + "-" * 80)
print("EMAIL BODY:")
print("-" * 80 + "\n")
print(build_role_change_email(EMPLOYEE))
print("\n" + "-" * 80)
print("\n" + "=" * 80)
print("Ready to send to Ahwaz Akhtar with Contract + NDA attached")
print("=" * 80)
