#!/usr/bin/env python3
"""Send fellowship offer email to Muhammad Ahmed with contract and NDA PDFs."""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from hr_assistant.config import get_google_services
from hr_assistant.audit_log import log as audit_log

CANDIDATE = {
    "name": "Muhammad Ahmed",
    "first_name": "Muhammad",
    "position": "AI Engineer Intern (Fellowship)",
    "start_date": "Monday, 1st of June 2026",
    "company": "Taleemabad, powered by Orenda",
    "compensation": "40",
    "employment_type": "full-time, fellowship-based",
    "email": "muhammadfgs7@gmail.com",
}

CC_RECIPIENTS = [
    "hr@taleemabad.com",
    "hiring@taleemabad.com",
    "accounts.query@taleemabad.com",
    "mashhood.ali.rastgar@taleemabad.com",
]

# Contract and NDA doc IDs
CONTRACT_ID = "1a04rVQqmDSz_PQp1NPq3hfI2pm-uYg3uv_eZe67LF8o"
NDA_ID = "1tPjZBTbpDP2wO_FOpNO-Dq3xsGgIM4jXxJzW4hedXxE"

ONBOARDING_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSf70SM4jlx4muDMLlN1ZMqHqVEQjJQgCBga-oRM-M1OZXCePw/viewform?usp=sharing&ouid=108638480093303713396&urp=gmail_link"
WHATSAPP_LINK = "https://chat.whatsapp.com/HglkfuENmLqEbaq8N5jSVq"

_SENDER_SIGNATURE = """\
<span class="gmail_signature_prefix">-- </span><br>\
<div dir="ltr" class="gmail_signature"><div dir="ltr">\
<b style="color:rgb(34,34,34)"><font color="#6aa84f">Oreo</font></b>\
<div style="color:rgb(34,34,34)"><b><font color="#3d85c6">Ayat's Personal AI Assistant -- Taleemabad</font></b></div>\
</div></div>"""

def build_email_body(candidate: dict) -> str:
    """Build HTML email body."""
    return (
        f'<div dir="ltr"><font color="#000000">'
        f'<span style="background-color:rgb(255,255,255)">Dear {candidate["first_name"]},</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">I hope you read this in good health and high spirits.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">We are pleased to announce that you have been selected for the position of <b>{candidate["position"]}</b> at <b>{candidate["company"]}</b>, starting <b>{candidate["start_date"]}</b>. Your monthly compensation for this <b>{candidate["employment_type"]}</b> role is <b>PKR {candidate["compensation"]},000</b>, inclusive of taxes.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Please find the <b>Contract</b> and <b>Non-Disclosure Agreement (NDA)</b> attached to this email.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Additionally, please take note of the essential logistical requirements outlined below:</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Complete the form linked here with your information for record-keeping purposes and upload your educational documents, signed contracts, a signed NDA, and an experience letter: <a href="{ONBOARDING_FORM}" target="_blank">Click here</a></span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Provide your bank name, account title, and IBAN number, matching the details on your cheque book. Upon the submission of all required documents, we will proceed to set up your teams and email ID.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Join the <b>Orenda | Taleemabad WhatsApp Group</b> via the following link: <a href="{WHATSAPP_LINK}" target="_blank">Click Here</a></span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Once you are officially registered in the company records, you will receive an HR portal account activation email.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Welcome to the team once again!</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">Should you have any queries or concerns, please feel free to reach out to the HR team.</span>'
        f'</font></div>'
        f'{_SENDER_SIGNATURE}</div>'
    )

def send_fellowship_offer(drive, gmail, candidate: dict, contract_id: str, nda_id: str, cc_list: list):
    """Send fellowship offer email with contract and NDA PDFs."""
    name = candidate["name"]
    to_address = candidate["email"]
    subject = f"Welcome to Taleemabad - {candidate['position']}"

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
    msg["From"] = "ayat@niete.edu.pk"
    msg["To"] = to_address
    msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = subject
    msg.attach(MIMEText(build_email_body(candidate), "html"))

    # Attach Contract PDF
    contract_part = MIMEApplication(contract_pdf, _subtype="pdf")
    contract_part.add_header(
        "Content-Disposition", "attachment",
        filename=f"{name} - Contract.pdf"
    )
    msg.attach(contract_part)

    # Attach NDA PDF
    nda_part = MIMEApplication(nda_pdf, _subtype="pdf")
    nda_part.add_header(
        "Content-Disposition", "attachment",
        filename=f"{name} - NDA.pdf"
    )
    msg.attach(nda_part)

    # Send email
    print(f"\nSending email to {to_address}...")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = gmail.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    print(f"✓ Email sent successfully!")
    audit_log("EMAIL_SENT", f"to={to_address} cc={cc_list} subject='{subject}' type=FELLOWSHIP_OFFER")

    return {
        "message_id": result["id"],
        "subject": subject,
        "to": to_address,
        "cc": cc_list,
    }

def main():
    print("=" * 100)
    print("SENDING FELLOWSHIP OFFER EMAIL - MUHAMMAD AHMED")
    print("=" * 100)

    services = get_google_services()
    drive = services["drive"]
    gmail = services["gmail"]

    print(f"\nCandidate: {CANDIDATE['name']}")
    print(f"Email: {CANDIDATE['email']}")
    print(f"Position: {CANDIDATE['position']}")
    print(f"CC Recipients: {len(CC_RECIPIENTS)}")
    print()

    result = send_fellowship_offer(drive, gmail, CANDIDATE, CONTRACT_ID, NDA_ID, CC_RECIPIENTS)

    print("\n" + "=" * 100)
    print("EMAIL SENT SUCCESSFULLY!")
    print("=" * 100)
    print(f"\nSubject: {result['subject']}")
    print(f"Sent To: {result['to']}")
    print(f"\nCC'd to:")
    for i, cc in enumerate(result['cc'], 1):
        print(f"  {i}. {cc}")
    print(f"\nAttachments:")
    print(f"  - Muhammad Ahmed - Contract.pdf")
    print(f"  - Muhammad Ahmed - NDA.pdf")
    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
