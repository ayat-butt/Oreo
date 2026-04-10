"""
Contract drafting service.

Copies the right template pair (contract + NDA) into a per-employee Drive folder,
fills every placeholder, removes template highlights, bolds key fields,
and returns links for preview — nothing is shared until you approve.
"""

from __future__ import annotations
from datetime import datetime
from googleapiclient.discovery import Resource
from hr_assistant.audit_log import log as audit_log

# ── Template document IDs (source templates — never modified) ─────────────────
TEMPLATE_IDS: dict[str, str] = {
    "owt_full_time":  "1cR_EqQuz3K1UOJNDD2H2cX3HAz7UNpwVxFIL6lQoEpk",
    "owt_project":    "1UdhLev16UqJVGgFG30lYzf3taK1QXTUZTTnLAa83Wuk",
    "opl_full_time":  "1HOtd_TczaGJiZa5fUkIkvYTO30f0qsEj_UbjtWwUED8",
    "opl_project":    "11r1lzHghTJ0acvHY_5zBoSoBaOEC4rj-BAx59ARop5Q",
    "taleemabad":     "1M3ESSBIw5INc6UVM0s6f_OrvK9A43pwfjb9ZCaErTNs",
    "addendum":       "15fJFuN870tSuDqkzt2KcGXPpUDsePwMfHXZg08Fs6PU",
    "nda_full_time":  "1A-Mokho52x0WJcGhwDEbTY6jGVxNkc7sKfWf57BREPY",
    "nda_project":    "1E70phwY-AV1Jfzu4PvUwrZjNXXMmNQNeHbyO84kEtjc",
}

# ── Contract + NDA pairing ────────────────────────────────────────────────────
CONTRACT_PAIRS: dict[tuple[str, str], tuple[str, str | None]] = {
    ("owt",        "full_time"):  ("owt_full_time", "nda_full_time"),
    ("owt",        "project"):    ("owt_project",   "nda_project"),
    ("owt",        "part_time"):  ("owt_project",   "nda_project"),
    ("opl",        "full_time"):  ("opl_full_time", "nda_full_time"),
    ("opl",        "project"):    ("opl_project",   "nda_project"),
    ("opl",        "part_time"):  ("opl_project",   "nda_project"),
    ("taleemabad", "full_time"):  ("taleemabad",    "nda_full_time"),
    ("taleemabad", "project"):    ("taleemabad",    "nda_full_time"),
    ("taleemabad", "part_time"):  ("taleemabad",    "nda_full_time"),
    ("orenda",     "addendum"):   ("addendum",      None),
}

PARENT_FOLDER_NAME = "CONTRACT FOR AGENT OREO"


# ── Drive helpers ─────────────────────────────────────────────────────────────

def _get_or_create_parent_folder(drive: Resource) -> str:
    results = drive.files().list(
        q=(f"name='{PARENT_FOLDER_NAME}' "
           "and mimeType='application/vnd.google-apps.folder' "
           "and trashed=false"),
        fields="files(id, name)",
    ).execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    folder = drive.files().create(
        body={"name": PARENT_FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"},
        fields="id",
    ).execute()
    print(f"  Created Drive folder: {PARENT_FOLDER_NAME}")
    return folder["id"]


def _create_employee_folder(drive: Resource, parent_id: str, emp: dict) -> str:
    folder_name = f"{emp['name']} - {emp['joining_date']}"
    folder = drive.files().create(
        body={
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        },
        fields="id",
    ).execute()
    return folder["id"]


def _copy_template(drive: Resource, template_id: str, title: str, folder_id: str) -> str:
    copy = drive.files().copy(
        fileId=template_id,
        body={"name": title, "parents": [folder_id]},
    ).execute()
    return copy["id"]


# ── Docs formatting helpers ───────────────────────────────────────────────────

def _apply_replacements(docs: Resource, doc_id: str, pairs: list[tuple[str, str]]) -> None:
    """Run replaceAllText for every (find, replace) pair in one batchUpdate."""
    requests = [
        {
            "replaceAllText": {
                "containsText": {"text": find, "matchCase": True},
                "replaceText": replace,
            }
        }
        for find, replace in pairs
        if find
    ]
    if requests:
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()


def _remove_highlights(docs: Resource, doc_id: str) -> None:
    """Strip all text background colours (template guidance markers)."""
    doc = docs.documents().get(documentId=doc_id).execute()
    end = doc["body"]["content"][-1]["endIndex"] - 1
    if end < 2:
        return
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{
            "updateTextStyle": {
                "range": {"startIndex": 1, "endIndex": end},
                "textStyle": {"backgroundColor": {}},
                "fields": "backgroundColor",
            }
        }]},
    ).execute()


def _bold_fields(docs: Resource, doc_id: str, values: list[str]) -> None:
    """Bold every occurrence of each value string in the document."""
    doc = docs.documents().get(documentId=doc_id).execute()
    requests = []

    def walk(elements):
        for el in elements:
            if "paragraph" in el:
                for pe in el["paragraph"].get("elements", []):
                    text  = pe.get("textRun", {}).get("content", "")
                    start = pe.get("startIndex", 0)
                    for val in values:
                        if not val or len(val) < 3:
                            continue
                        idx = text.find(val)
                        while idx != -1:
                            requests.append({
                                "updateTextStyle": {
                                    "range": {
                                        "startIndex": start + idx,
                                        "endIndex":   start + idx + len(val),
                                    },
                                    "textStyle": {"bold": True},
                                    "fields": "bold",
                                }
                            })
                            idx = text.find(val, idx + 1)
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        walk(cell.get("content", []))

    walk(doc["body"]["content"])
    for i in range(0, len(requests), 50):
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests[i:i+50]}
        ).execute()


# ── JD extraction helpers ─────────────────────────────────────────────────────

_JD_SECTIONS = {"Key Responsibilities"}


def _extract_jd_lines(docs: Resource, jd_doc_id: str) -> list[str]:
    """Read a JD Google Doc and return bullet lines for Key Responsibilities and related sections."""
    doc = docs.documents().get(documentId=jd_doc_id).execute()
    lines = []
    in_section = False
    last_section = None

    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        style = el["paragraph"].get("paragraphStyle", {}).get("namedStyleType", "")
        is_heading = style in ("HEADING_2", "HEADING_3")
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        ).strip()
        if not text:
            continue

        if is_heading:
            if text in _JD_SECTIONS:
                in_section = True
                last_section = text
            elif in_section and style == "HEADING_3":
                lines.append(f"\n{text}:")
            elif in_section and style == "HEADING_2":
                # New top-level section — stop extracting
                in_section = False
        elif in_section and el["paragraph"].get("bullet"):
            lines.append(f"\u2022 {text}")

    return [l for l in lines if l.strip()]


def _insert_jd_into_annexure(docs: Resource, contract_id: str, jd_lines: list[str]) -> None:
    """Insert JD bullet lines after the 'Key Responsibilities' heading in Annexure A."""
    if not jd_lines:
        return
    doc = docs.documents().get(documentId=contract_id).execute()
    insert_idx = None
    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        ).strip()
        if text in ("Key Responsibilities", "Key Responsibilities:", "Job Description:", "Job Description"):
            insert_idx = el["endIndex"]
            break
    if insert_idx is None:
        return
    jd_text = "\n".join(jd_lines) + "\n"
    docs.documents().batchUpdate(
        documentId=contract_id,
        body={"requests": [{"insertText": {"location": {"index": insert_idx}, "text": "\n" + jd_text}}]},
    ).execute()


def _fill_header_date(docs: Resource, contract_id: str, date_str: str) -> None:
    """Insert the date into the blank date cell in the contract header, then bold it."""
    doc = docs.documents().get(documentId=contract_id).execute()
    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        si = el.get("startIndex", 0)
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        )
        if text.startswith("Date: ") and "Private & Confidential" in text:
            after_label = text[6:]
            if after_label.startswith("\t") or after_label.startswith("P"):
                insert_at = si + 6
                docs.documents().batchUpdate(
                    documentId=contract_id,
                    body={"requests": [
                        {"insertText": {"location": {"index": insert_at}, "text": date_str}},
                    ]},
                ).execute()
                # Bold the inserted date to match Name / CNIC formatting
                docs.documents().batchUpdate(
                    documentId=contract_id,
                    body={"requests": [{
                        "updateTextStyle": {
                            "range": {"startIndex": insert_at, "endIndex": insert_at + len(date_str)},
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }
                    }]},
                ).execute()
            break


def _fill_offer_acceptance(docs: Resource, contract_id: str, name: str, cnic: str) -> None:
    """Replace the NAME / CNIC XYZ placeholders in the Offer Acceptance section.
    Handles both OPL variant ('I, NAME , the employee, bearing CNIC XYZ')
    and OWT variant ('I, XYZ, the Employee bearing CNIC XYZ.').
    """
    requests = [
        # OPL full-time variant
        {
            "replaceAllText": {
                "containsText": {"text": "I, NAME , the employee, bearing CNIC XYZ", "matchCase": True},
                "replaceText": f"I, {name} , the employee, bearing CNIC {cnic}",
            }
        },
        # OWT full-time variant
        {
            "replaceAllText": {
                "containsText": {"text": "I, XYZ, the Employee bearing CNIC XYZ.", "matchCase": True},
                "replaceText": f"I, {name}, the Employee bearing CNIC {cnic}.",
            }
        },
    ]
    docs.documents().batchUpdate(
        documentId=contract_id,
        body={"requests": requests},
    ).execute()


# ── Salutation + joining line helpers ─────────────────────────────────────────

def _salutation(emp: dict) -> str:
    """Return Miss / Mr. based on gender field."""
    gender = emp.get("gender", "").lower().strip()
    if gender in ("female", "f", "woman"):
        return "Miss"
    return "Mr."


def _joining_line(emp: dict) -> str:
    """Build the joining arrangement sentence when both dates are supplied."""
    remote   = emp.get("remote_date", "")
    inperson = emp.get("inperson_date", "")
    if remote and inperson:
        return (
            f" Your joining arrangement is as follows: "
            f"remote working commences {remote}, "
            f"followed by in-person office attendance from {inperson}."
        )
    return ""


# ── Placeholder maps per template ─────────────────────────────────────────────

def _replacements(template_key: str, emp: dict) -> list[tuple[str, str]]:
    name         = emp["name"]
    cnic         = emp["cnic"]
    designation  = emp["designation"]
    department   = emp["department"]
    salary       = emp["salary"]
    joining_date = emp["joining_date"]
    today        = datetime.now().strftime("%d %B %Y")
    start_date   = emp.get("start_date", joining_date)
    end_date     = emp.get("end_date", "")
    duration     = emp.get("duration", "")
    sal          = _salutation(emp)
    j_line       = _joining_line(emp)

    # ── NDAs ─────────────────────────────────────────────────────────────────
    if template_key in ("nda_full_time", "nda_project"):
        return [
            ("EMPLOYEE NAME", name),
            ("JOINING DATE",  joining_date),
            ("CURRENT DATE",  today),   # employer signature date; employee date left blank
        ]

    # ── OWT Full Time ─────────────────────────────────────────────────────────
    if template_key == "owt_full_time":
        return [
            ("Pakistan Date:",                           f"Pakistan Date: {today}"),
            ("Private & Confidential CNIC: ",            f"Private & Confidential CNIC: {cnic}"),
            ("Name: ",                                   f"Name: {name}"),
            ("Mr./Ms. XYZ (Hereinafter, referred to as",
             f"{sal} {name} (Hereinafter, referred to as"),
            (
                "position XYZ in the XYZ Department on behalf of Orenda Welfare Trust",
                f"position {designation} in the {department} Department on behalf of Orenda Welfare Trust",
            ),
            ("with effect from XYZ.",                   f"with effect from {joining_date}.{j_line}"),
            ("PKR XYZ/month",                           f"PKR {salary}/month"),
        ]

    # ── OPL Full Time ─────────────────────────────────────────────────────────
    if template_key == "opl_full_time":
        return [
            ("Pakistan Date:",                           f"Pakistan Date: {today}"),
            ("Private & Confidential CNIC: ",            f"Private & Confidential CNIC: {cnic}"),
            ("Name: ",                                   f"Name: {name}"),
            ("Mr. / Ms. XYZ (hereinafter referred to as",
             f"{sal} {name} (hereinafter referred to as"),
            (
                "position of XYZ as part of the XYZ Team of Orenda Private Limited",
                f"position of {designation} as part of the {department} Team of Orenda Private Limited",
            ),
            ('effect from XYZ (the "Commencement Date").',
             f'effect from {joining_date} (the "Commencement Date").{j_line}'),
            ("PKR XYZ /month",                          f"PKR {salary} /month"),
        ]

    # ── OWT Project / Part Time ───────────────────────────────────────────────
    if template_key == "owt_project":
        return [
            ("Pakistan Date:",                           f"Pakistan Date: {today}"),
            ("Private & Confidential           CNIC:",   f"Private & Confidential CNIC: {cnic}"),
            ("Name: ",                                   f"Name: {name}"),
            ("Mr./ Ms. XYZ bearing CNIC NoXYZ",
             f"{sal} {name} bearing CNIC No{cnic}"),
            ("day of MONTH, YEAR to day of MONTH , YEAR", f"{start_date} to {end_date}"),
            ("contract with a duration of XYZ months",  f"contract with a duration of {duration} months"),
        ]

    # ── OPL Project Based ─────────────────────────────────────────────────────
    if template_key == "opl_project":
        return [
            ("Current Date",                             today),
            ("EMPLOYEE'S CNIC",                          cnic),
            ("EMPLOYEE'S NAME",                          name),
            ("EMPLOYEE NAME",                            name),
            ("EFFECTIVE DATE OF JOINING",                joining_date),
            ("DATE,MONTH, YEAR to DATE, MONTH , YEAR",  f"{start_date} to {end_date}"),
            ("contract with a duration of XYZ",         f"contract with a duration of {duration}"),
        ]

    # ── Taleemabad Inc ────────────────────────────────────────────────────────
    if template_key == "taleemabad":
        return [
            ("CURRENT DATE",                             today),
            ("EMPLOYEE NAME",                            name),
            ("Date Month, Year",                         joining_date),
            (f'XYZ as a "Designation"',                  f'{name} as a "{designation}"'),
            ("PKR XYZ/ per month",                       f"PKR {salary}/ per month"),
            ("X-Y-Z",                                    cnic),
        ]

    # ── Addendum / Extension ──────────────────────────────────────────────────
    if template_key == "addendum":
        prev_date = emp.get("prev_contract_date", "")
        return [
            ("PREVIOUS CONTRACT DATE",                   prev_date),
            ("Mr./ Ms. XYZ, an Employee at Orenda",
             f"Mr./ Ms. {name}, an Employee at Orenda"),
            ("fromXYZ  till XYZ",                        f"from {joining_date} till {end_date}"),
            ("asDESIGNATION",                            f"as {designation}"),
            ("I, XYZ,  bearing CNIC XYZ",
             f"I, {name},  bearing CNIC {cnic}"),
        ]

    return []


# ── Main entry point ──────────────────────────────────────────────────────────

def draft_contracts(drive: Resource, docs: Resource, emp: dict) -> dict:
    """
    Draft contract + NDA for a new hire.
    Removes template highlights and bolds all key fields automatically.
    Returns doc links for preview — nothing is shared until you approve.

    emp dict keys
    ─────────────
    Required:   name, cnic, designation, department, salary,
                joining_date, entity, employment_type

    Optional:   gender          "male" | "female"  (default: male → Mr.)
                remote_date     e.g. "07 April 2026"
                inperson_date   e.g. "15 April 2026"
                start_date      project contracts
                end_date        project / addendum
                duration        project contracts (months as string)
                prev_contract_date  addendum only
                hod_name        Head of Department name for signing section
                hod_designation Head of Department designation
                jd_doc_id       Google Doc ID of the Job Description (fills Annexure A)

    entity:          "owt" | "opl" | "taleemabad" | "orenda"
    employment_type: "full_time" | "project" | "part_time" | "addendum"
    """
    entity   = emp["entity"].lower().strip()
    emp_type = emp["employment_type"].lower().strip()

    pair_key = (entity, emp_type)
    if pair_key not in CONTRACT_PAIRS:
        raise ValueError(
            f"No template pair for entity='{entity}', type='{emp_type}'.\n"
            f"Valid combinations: {list(CONTRACT_PAIRS.keys())}"
        )

    contract_key, nda_key = CONTRACT_PAIRS[pair_key]

    # Values to bold (skip blanks and very short strings)
    # Use "Miss/Mr. Name" as the bold target — NOT the full sentence with parentheticals
    sal = _salutation(emp)
    bold_values = [
        v for k in ("cnic", "designation", "department", "salary",
                    "joining_date", "remote_date", "inperson_date")
        if (v := emp.get(k, "")) and len(v) > 2
    ]
    # Bold salutation + name (e.g. "Miss Ayat Butt") and bare name (e.g. "Ayat Butt" in Offer Acceptance)
    bold_values.append(f"{sal} {emp['name']}")
    bold_values.append(emp["name"])

    # OPL-specific: bold entity name and "{department} Team" phrase
    if contract_key in ("opl_full_time", "opl_project"):
        dept = emp.get("department", "")
        if dept:
            bold_values.append(f"{dept} Team")
        bold_values.append("Orenda Private Limited")

    # 1. Ensure parent folder
    parent_id = _get_or_create_parent_folder(drive)

    # 2. Employee sub-folder
    emp_folder_id = _create_employee_folder(drive, parent_id, emp)
    print(f"  Created folder: {emp['name']} - {emp['joining_date']}")

    # 3. Contract: copy → fill → remove highlights → bold
    contract_title = f"{emp['name']} - Contract"
    contract_id = _copy_template(drive, TEMPLATE_IDS[contract_key], contract_title, emp_folder_id)
    _apply_replacements(docs, contract_id, _replacements(contract_key, emp))
    _remove_highlights(docs, contract_id)
    _bold_fields(docs, contract_id, bold_values)

    # 3a. Fill header date (OPL/OWT full-time templates have a blank date cell)
    today_str = datetime.now().strftime("%d %B %Y")
    _fill_header_date(docs, contract_id, today_str)

    # 3b. Fill offer acceptance section (NAME / CNIC XYZ placeholders)
    _fill_offer_acceptance(docs, contract_id, emp["name"], emp["cnic"])

    # 3c. Fill HoD signing section if provided (name, designation, and today's date)
    hod_name = emp.get("hod_name", "")
    hod_designation = emp.get("hod_designation", "")
    if hod_name or hod_designation:
        hod_pairs = []
        if hod_name:
            # OPL uses "Head of Department's Name", OWT uses "HOD Name"
            hod_pairs.append(("Head of Department's Name", hod_name))
            hod_pairs.append(("HOD Name", hod_name))
        if hod_designation:
            hod_pairs.append(("Designation", hod_designation))
        # Always fill the HoD date with today's date
        hod_pairs.append(("Date", today_str))
        _apply_replacements(docs, contract_id, hod_pairs)

    # 3d. Insert JD into Annexure A if a JD doc ID is provided
    jd_doc_id = emp.get("jd_doc_id", "")
    if jd_doc_id:
        jd_lines = _extract_jd_lines(docs, jd_doc_id)
        _insert_jd_into_annexure(docs, contract_id, jd_lines)
        print(f"  Inserted JD ({len(jd_lines)} lines) into Annexure A")

    print(f"  Drafted contract:  {contract_title}")
    audit_log("CONTRACT_CREATED", f"employee='{emp['name']}' entity={entity} type={emp_type} doc_id={contract_id}")

    # 4. NDA: copy → fill → remove highlights → bold
    nda_id  = None
    nda_url = None
    if nda_key:
        nda_title = f"{emp['name']} - NDA"
        nda_id = _copy_template(drive, TEMPLATE_IDS[nda_key], nda_title, emp_folder_id)
        _apply_replacements(docs, nda_id, _replacements(nda_key, emp))
        _remove_highlights(docs, nda_id)
        _bold_fields(docs, nda_id, bold_values)
        print(f"  Drafted NDA:       {nda_title}")
        audit_log("NDA_CREATED", f"employee='{emp['name']}' doc_id={nda_id}")
        nda_url = f"https://docs.google.com/document/d/{nda_id}/edit"

    return {
        "employee":     emp["name"],
        "folder_url":   f"https://drive.google.com/drive/folders/{emp_folder_id}",
        "contract_url": f"https://docs.google.com/document/d/{contract_id}/edit",
        "nda_url":      nda_url,
    }
