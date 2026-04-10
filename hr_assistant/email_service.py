"""
Welcome email drafting service.

Exports the Contract and NDA from Google Docs as PDFs, builds the
standard welcome email from the employee dict, and saves it as a
Gmail draft for review before sending.

Nothing is sent until you open Gmail Drafts and send it manually.
"""

from __future__ import annotations
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from googleapiclient.discovery import Resource
from hr_assistant.audit_log import log as audit_log


# ── Hard allowlist — Oreo may only send to these domains ─────────────────────
_ALLOWED_DOMAINS = {"taleemabad.com", "niete.edu.pk", "niete.pk"}

def _assert_allowed(address: str) -> None:
    """Block any send attempt to an address outside the approved domains."""
    domain = address.strip().lower().split("@")[-1]
    if domain not in _ALLOWED_DOMAINS:
        raise ValueError(
            f"SECURITY BLOCK: '{address}' is not in the approved domain list "
            f"{_ALLOWED_DOMAINS}. Oreo cannot send emails outside Taleemabad / NIETE."
        )


# ── Fixed links (same across all Taleemabad hires) ───────────────────────────
_ONBOARDING_FORM = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSf70SM4jlx4muDMLlN1ZMqHqVEQjJQgCBga-oRM-M1OZXCePw/viewform"
)
_WHATSAPP_LINK = "https://chat.whatsapp.com/HglkfuENmLqEbaq8N5jSVq"
_SENDER_SIGNATURE = """\
<span class="gmail_signature_prefix">-- </span><br>\
<div dir="ltr" class="gmail_signature"><div dir="ltr">\
<b style="color:rgb(34,34,34)"><font color="#6aa84f">Oreo</font></b>\
<div style="color:rgb(34,34,34)"><b><font color="#3d85c6">Ayat&#39;s Personal AI Assistant — Taleemabad</font></b></div>\
</div></div>"""


def _build_email_body(emp: dict) -> str:
    """Build the HTML body of the welcome email from employee details."""
    first_name    = emp["name"].split()[0]
    designation   = emp["designation"]
    joining_date  = emp["joining_date"]   # displayed as effective/start date
    salary        = emp["salary"]
    remote_date   = emp.get("remote_date", "")
    inperson_date = emp.get("inperson_date", "")

    # Joining arrangement line
    if remote_date and inperson_date:
        arrangement = (
            f"<p>Your joining arrangement is as follows: you will begin working "
            f"<b>remotely from {remote_date}</b>, followed by "
            f"<b>in-person office attendance from {inperson_date}</b>.</p>"
        )
    else:
        arrangement = ""

    return (
        f'<div dir="ltr"><font color="#000000">'
        f'<span style="background-color:rgb(255,255,255)">Hi {first_name},</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">I hope this email finds you in great health and high spirits.</span><br><br>'
        f'<span style="background-color:rgb(255,255,255)">On behalf of all of us at <b>Taleemabad</b>, we are delighted to welcome you '
        f'to the team as <b>{designation}</b>, effective <b>{joining_date},</b> with a total monthly compensation of '
        f'<b>PKR {salary} (gross)</b>. We\'re excited to have you onboard and look forward to the impact you will create.</span>'
        f'</font><div><font color="#000000"><span style="background-color:rgb(255,255,255)"><br>'
        + (
            f'Your joining arrangement is as follows: you will begin working <b>remotely from {remote_date}</b>, '
            f'followed by <b>in-person office attendance from {inperson_date}</b>.<br><br>'
            if remote_date and inperson_date else ''
        ) +
        f'Please find the <b>Contract</b> and <b>Non-Disclosure Agreement (NDA)</b> attached to this email. '
        f'Kindly download, sign, and return both documents as attachments in your reply.<br><br>'
        f'Additionally, please take note of the essential logistical requirements outlined below:<br><br>'
        f'Complete the form linked here with your information for record-keeping purposes and upload your educational '
        f'documents, signed contracts, a signed NDA, and an experience letter: '
        f'<a href="{_ONBOARDING_FORM}" target="_blank">Click here</a><br><br>'
        f'Provide your bank name, account title, and IBAN number, matching the details on your cheque book. '
        f'Upon the submission of all required documents, we will proceed to set up your teams and email ID.<br><br>'
        f'Join the <b>Orenda | Taleemabad WhatsApp Group</b> via the following link: '
        f'<a href="{_WHATSAPP_LINK}" target="_blank">Click Here</a><br><br>'
        f'Once you are officially registered in the company records, you will receive an HR portal account activation email.<br><br>'
        f'Welcome to the team once again, {first_name}!<br><br>'
        f'Should you have any queries or concerns, please feel free to reach out to the HR team.'
        f'</span></font></div>'
        f'<div><font color="#000000"><span style="background-color:rgb(255,255,255)"><br></span></font></div>'
        f'<div><font color="#000000"><span style="background-color:rgb(255,255,255)">Warm regards,</span></font></div>'
        f'{_SENDER_SIGNATURE}</div>'
    )


def draft_welcome_email(
    drive: Resource,
    gmail: Resource,
    emp: dict,
    contract_id: str,
    nda_id: str | None,
    cc: list[str] | None = None,
    subject_prefix: str = "",
) -> dict:
    """
    Export Contract (+NDA) as PDFs, build the welcome email, save as Gmail draft.

    emp dict keys used:
        name, designation, salary, joining_date
        remote_date, inperson_date  (optional — adds joining arrangement line)
        email                       (recipient address)

    cc             — optional list of CC addresses
    subject_prefix — e.g. "[TEST] " prepended to the subject line

    Returns dict with draft_id and subject.
    Nothing is sent — open Gmail Drafts to review and send manually.
    """
    name       = emp["name"]
    to_address = emp["email"]
    subject    = f"{subject_prefix}Welcome to Taleemabad - {emp['designation']}"

    # ── Hard allowlist check — raises immediately if domain not approved ──────
    _assert_allowed(to_address)
    for cc_addr in (cc or []):
        _assert_allowed(cc_addr)

    # ── Export PDFs ───────────────────────────────────────────────────────────
    print("  Exporting Contract as PDF...")
    contract_pdf = drive.files().export(
        fileId=contract_id, mimeType="application/pdf"
    ).execute()

    nda_pdf = None
    if nda_id:
        print("  Exporting NDA as PDF...")
        nda_pdf = drive.files().export(
            fileId=nda_id, mimeType="application/pdf"
        ).execute()

    # ── Build MIME message ────────────────────────────────────────────────────
    msg = MIMEMultipart()
    msg["To"]      = to_address
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg.attach(MIMEText(_build_email_body(emp), "html"))

    contract_part = MIMEApplication(contract_pdf, _subtype="pdf")
    contract_part.add_header(
        "Content-Disposition", "attachment",
        filename=f"{name} - Contract.pdf"
    )
    msg.attach(contract_part)

    if nda_pdf:
        nda_part = MIMEApplication(nda_pdf, _subtype="pdf")
        nda_part.add_header(
            "Content-Disposition", "attachment",
            filename=f"{name} - NDA.pdf"
        )
        msg.attach(nda_part)

    # ── Save as Gmail draft ───────────────────────────────────────────────────
    raw   = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = gmail.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()

    print(f"  Gmail draft saved: '{subject}' → {to_address}")
    audit_log("EMAIL_DRAFTED", f"to={to_address} cc={cc or []} subject='{subject}'")
    return {
        "draft_id": draft["id"],
        "subject":  subject,
        "to":       to_address,
    }
