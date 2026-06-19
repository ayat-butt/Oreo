#!/usr/bin/env python3
"""Draft welcome email for Muhammad Ahmed - Fellowship/Internship."""

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
}

# Fixed links
ONBOARDING_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSf70SM4jlx4muDMLlN1ZMqHqVEQjJQgCBga-oRM-M1OZXCePw/viewform?usp=sharing&ouid=108638480093303713396&urp=gmail_link"
WHATSAPP_LINK = "https://chat.whatsapp.com/HglkfuENmLqEbaq8N5jSVq"

_SENDER_SIGNATURE = """\
<span class="gmail_signature_prefix">-- </span><br>\
<div dir="ltr" class="gmail_signature"><div dir="ltr">\
<b style="color:rgb(34,34,34)"><font color="#6aa84f">Oreo</font></b>\
<div style="color:rgb(34,34,34)"><b><font color="#3d85c6">Ayat's Personal AI Assistant -- Taleemabad</font></b></div>\
</div></div>"""

def build_welcome_email(candidate: dict) -> str:
    """Build welcome email matching the provided template."""
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

def main():
    print("=" * 100)
    print("WELCOME EMAIL DRAFT - MUHAMMAD AHMED")
    print("=" * 100)
    print(f"\nFrom:    Ayat Butt <ayat@niete.edu.pk>")
    print(f"To:      Muhammad Ahmed <[EMAIL PENDING]>")
    print(f"Subject: Welcome to Taleemabad - {CANDIDATE['position']}")
    print(f"\nAttachments:")
    print(f"  - Muhammad Ahmed - Contract.pdf")
    print(f"  - Muhammad Ahmed - NDA.pdf")
    print("\n" + "-" * 100)
    print("EMAIL BODY:")
    print("-" * 100 + "\n")

    email_body = build_welcome_email(CANDIDATE)

    # Print as plain text for readability
    plain_text = (
        f"Dear {CANDIDATE['first_name']},\n\n"
        f"I hope you read this in good health and high spirits.\n\n"
        f"We are pleased to announce that you have been selected for the position of {CANDIDATE['position']} at {CANDIDATE['company']}, starting {CANDIDATE['start_date']}. Your monthly compensation for this {CANDIDATE['employment_type']} role is PKR {CANDIDATE['compensation']},000, inclusive of taxes.\n\n"
        f"Please find the Contract and Non-Disclosure Agreement (NDA) attached to this email.\n\n"
        f"Additionally, please take note of the essential logistical requirements outlined below:\n\n"
        f"Complete the form linked here with your information for record-keeping purposes and upload your educational documents, signed contracts, a signed NDA, and an experience letter: Click here\n\n"
        f"Provide your bank name, account title, and IBAN number, matching the details on your cheque book. Upon the submission of all required documents, we will proceed to set up your teams and email ID.\n\n"
        f"Join the Orenda | Taleemabad WhatsApp Group via the following link: Click Here\n\n"
        f"Once you are officially registered in the company records, you will receive an HR portal account activation email.\n\n"
        f"Welcome to the team once again!\n\n"
        f"Should you have any queries or concerns, please feel free to reach out to the HR team.\n\n"
        f"Warm regards,\n"
        f"Oreo\n"
        f"Ayat's Personal AI Assistant -- Taleemabad"
    )

    print(plain_text)
    print("\n" + "-" * 100)
    print("\n" + "=" * 100)
    print("EMAIL READY FOR REVIEW")
    print("=" * 100)

if __name__ == "__main__":
    main()
