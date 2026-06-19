#!/usr/bin/env python3
"""Draft customized role change/promotion email for existing employee."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from hr_assistant.config import get_google_services
from hr_assistant.audit_log import log as audit_log

EMPLOYEE = {
    "name": "Ahwaz Akhtar",
    "first_name": "Ahwaz",
    "email": "ahwaz.akhtar@taleemabad.com",
    "designation": "M&E Lead",
    "joining_date": "01 April 2026",
    "salary": "600,000",
    "previous_role": "Part-time Monitoring & Evaluation Officer (75%)",
    "new_employment": "Full-time, Permanent",
}

# Contract and NDA doc IDs
CONTRACT_ID = "1sXoOGFEuFuZoJndjppcTZR_IoGz3_YkhJ5oZLlMyIAY"
NDA_ID = "1KbSJVbM9iqkeuKRkjBAZmkYzp-29ygcWaymPYS3beoA"

_SENDER_SIGNATURE = """\
<span class="gmail_signature_prefix">-- </span><br>\
<div dir="ltr" class="gmail_signature"><div dir="ltr">\
<b style="color:rgb(34,34,34)"><font color="#6aa84f">Oreo</font></b>\
<div style="color:rgb(34,34,34)"><b><font color="#3d85c6">Ayat's Personal AI Assistant -- Taleemabad</font></b></div>\
</div></div>"""

def build_role_change_email(emp: dict) -> str:
    """Build HTML body for employment term change email."""
    first_name = emp["first_name"]
    designation = emp["designation"]
    joining_date = emp["joining_date"]
    salary = emp["salary"]
    new_employment = emp["new_employment"]

    return (
        f'<div dir="ltr"><font color="#000000">'
        f'<span style="background-color:rgb(255,255,255)">Hi {first_name},</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">We are delighted to confirm the updates to your employment terms, effective <b>{joining_date}</b>. '
        f'Your status will transition from part-time (75% capacity) to <b>{new_employment}</b>, in your role as <b>{designation}</b>, '
        f'with a revised monthly compensation of <b>PKR {salary} (gross)</b>.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Your continued dedication and excellent contributions have made you a valuable member of our team, '
        f'and we look forward to your continued growth and impact in this capacity.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Please find the updated <b>Contract</b> and <b>Non-Disclosure Agreement (NDA)</b> attached to this email. '
        f'Kindly review, sign, and return both documents as attachments in your reply.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">We already have your personal and employment details on file. '
        f'However, if there are any changes or updates needed to your records, please let us know in this email thread and we will ensure everything is updated accordingly.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Should you have any questions or concerns regarding your updated employment terms or compensation, '
        f'please feel free to reach out to the HR team.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Warm regards,</span></font></div>'
        f'{_SENDER_SIGNATURE}</div>'
    )


def draft_role_change_email(drive, gmail, emp: dict, contract_id: str, nda_id: str):
    """Draft employment term change email with updated contract and NDA."""
    name = emp["name"]
    to_address = emp["email"]
    subject = f"Confirmation of Updated Employment Terms - {emp['designation']}"

    print("Exporting Contract as PDF...")
    contract_pdf = drive.files().export(
        fileId=contract_id, mimeType="application/pdf"
    ).execute()

    print("Exporting NDA as PDF...")
    nda_pdf = drive.files().export(
        fileId=nda_id, mimeType="application/pdf"
    ).execute()

    # Build MIME message
    msg = MIMEMultipart()
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(build_role_change_email(emp), "html"))

    contract_part = MIMEApplication(contract_pdf, _subtype="pdf")
    contract_part.add_header(
        "Content-Disposition", "attachment",
        filename=f"{name} - Contract.pdf"
    )
    msg.attach(contract_part)

    nda_part = MIMEApplication(nda_pdf, _subtype="pdf")
    nda_part.add_header(
        "Content-Disposition", "attachment",
        filename=f"{name} - NDA.pdf"
    )
    msg.attach(nda_part)

    # Save as Gmail draft
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = gmail.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()

    print(f"Gmail draft saved: '{subject}' -> {to_address}")
    audit_log("EMAIL_DRAFTED", f"to={to_address} subject='{subject}' type=ROLE_CHANGE")

    return {
        "draft_id": draft["id"],
        "subject": subject,
        "to": to_address,
    }


def main():
    print("Connecting to Google services...")
    services = get_google_services()
    drive = services["drive"]
    gmail = services["gmail"]

    print(f"\nDrafting role change email for: {EMPLOYEE['name']}")
    print(f"New Role: {EMPLOYEE['designation']}")
    print(f"New Terms: {EMPLOYEE['new_employment']}")
    print(f"New Salary: PKR {EMPLOYEE['salary']}/month\n")

    result = draft_role_change_email(drive, gmail, EMPLOYEE, CONTRACT_ID, NDA_ID)

    print("\n" + "=" * 70)
    print("ROLE CHANGE EMAIL DRAFT CREATED")
    print("=" * 70)
    print(f"Subject: {result['subject']}")
    print(f"To:      {result['to']}")
    print(f"Status:  [DRAFT] Saved in Gmail Drafts")
    print(f"\nAttachments: Contract PDF + NDA PDF")
    print("=" * 70)
    print("\nEmail is ready for review. Check Gmail Drafts to preview.")


if __name__ == "__main__":
    main()
