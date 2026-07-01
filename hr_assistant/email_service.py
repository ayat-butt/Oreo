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


# ── Employee data-collection forms (chosen per hire, ALWAYS confirmed at send) ─
# Orenda form — OPL/OWT full-time & part-time employees.
_ORENDA_FORM = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSf70SM4jlx4muDMLlN1ZMqHqVEQjJQgCBga-oRM-M1OZXCePw/viewform"
)
# NIETE form — project-based roles (National Institute of Excellence in Teacher Education).
_NIETE_FORM = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSdVAYfCZZhusF_tNLn7mxzoK5BFXDa7xfj2FZifRlva-YDBHQ/viewform"
)
ONBOARDING_FORMS = {"orenda": _ORENDA_FORM, "niete": _NIETE_FORM}
_ONBOARDING_FORM = _ORENDA_FORM   # default when nothing chosen


def suggested_form_key(emp: dict) -> str:
    """Best-guess data form: project roles → NIETE; full/part-time → Orenda. Always confirmed."""
    return "niete" if (emp.get("employment_type", "") or "").lower() == "project" else "orenda"


def form_url(key: str | None) -> str:
    return ONBOARDING_FORMS.get((key or "").lower(), _ORENDA_FORM)


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
    onboarding_form = emp.get("onboarding_form", _ONBOARDING_FORM)

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
        f'<a href="{onboarding_form}" target="_blank">Click here</a><br><br>'
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


def _build_raw_message(
    drive: Resource,
    emp: dict,
    contract_id: str,
    nda_id: str | None,
    to_address: str,
    cc: list[str] | None,
    subject_prefix: str,
) -> tuple[str, str]:
    """Export Contract (+NDA) PDFs, build the MIME message, return (raw_base64, subject).

    Shared by both draft_welcome_email and send_welcome_email so the email is byte-identical
    whether drafted, piloted, or sent live. The sent PDFs are exported live from the docs here.
    """
    name    = emp["name"]
    subject = f"{subject_prefix}Welcome to Taleemabad - {emp['designation']}"

    contract_pdf = drive.files().export(fileId=contract_id, mimeType="application/pdf").execute()
    nda_pdf = drive.files().export(fileId=nda_id, mimeType="application/pdf").execute() if nda_id else None

    msg = MIMEMultipart()
    msg["To"]      = to_address
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg.attach(MIMEText(_build_email_body(emp), "html"))

    contract_part = MIMEApplication(contract_pdf, _subtype="pdf")
    contract_part.add_header("Content-Disposition", "attachment", filename=f"{name} - Contract.pdf")
    msg.attach(contract_part)
    if nda_pdf:
        nda_part = MIMEApplication(nda_pdf, _subtype="pdf")
        nda_part.add_header("Content-Disposition", "attachment", filename=f"{name} - NDA.pdf")
        msg.attach(nda_part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return raw, subject


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

    emp dict keys used: name, designation, salary, joining_date, email,
                        remote_date/inperson_date (optional).
    cc — optional CC list (allowlist-checked). subject_prefix — e.g. "[TEST] ".

    Returns {draft_id, subject, to}. Nothing is sent — review in Gmail Drafts.
    """
    to_address = emp["email"]
    # CC is allowlist-checked; To may be a personal candidate email (HR-authorized).
    for cc_addr in (cc or []):
        _assert_allowed(cc_addr)

    raw, subject = _build_raw_message(drive, emp, contract_id, nda_id, to_address, cc, subject_prefix)
    draft = gmail.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()

    print(f"  Gmail draft saved: '{subject}' -> {to_address}")
    audit_log("EMAIL_DRAFTED", f"to={to_address} cc={cc or []} subject='{subject}'")
    return {"draft_id": draft["id"], "subject": subject, "to": to_address}


def send_welcome_email(
    drive: Resource,
    gmail: Resource,
    emp: dict,
    contract_id: str,
    nda_id: str | None,
    cc: list[str] | None = None,
    subject_prefix: str = "",
    to_override: str | None = None,
) -> dict:
    """
    SEND the welcome email (contract + NDA attached) via Gmail.

    to_override — when set (PILOT/test), send here instead of the candidate; the test address
                  MUST be inside the approved domains. When None (LIVE), To is the candidate
                  (personal email allowed). CC is always allowlist-checked either way.

    Returns {message_id, subject, to}. This actually sends — gate it behind explicit confirmation.
    """
    to_address = to_override or emp["email"]
    if to_override:
        _assert_allowed(to_address)          # pilot/test must be an approved Taleemabad/NIETE address
    for cc_addr in (cc or []):
        _assert_allowed(cc_addr)

    raw, subject = _build_raw_message(drive, emp, contract_id, nda_id, to_address, cc, subject_prefix)
    sent = gmail.users().messages().send(userId="me", body={"raw": raw}).execute()

    kind = "PILOT" if to_override else "LIVE"
    print(f"  Email SENT ({kind}): '{subject}' -> {to_address}")
    audit_log("EMAIL_SENT", f"kind={kind} to={to_address} cc={cc or []} subject='{subject}' msg_id={sent.get('id')}")
    return {"message_id": sent["id"], "subject": subject, "to": to_address}
