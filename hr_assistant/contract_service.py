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

# ── Standard branded footer (applied to every generated contract) ─────────────
FOOTER_ADDRESS = (
    "2nd Floor, Time Square Plaza, Korang Road, "
    "I-10 Markaz, Islamabad | taleemabad.com"
)


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


def _bold_contract(docs: Resource, doc_id: str, emp: dict) -> None:
    """Bold contract fields per Ayat's standards — segment-aware, so the same value
    (e.g. the CNIC) is bold in some places and plain in others:

      • Header block  → bold the LABELS only (`Date:`, `CNIC:`, `Name:`), NOT the values
      • First paragraph → bold the name (salutation+name) only, plus designation, team,
                          "Orenda", and the effective date — never the bracketed text
      • Offer Acceptance → bold the employee name AND the CNIC number
      • Compensation   → bold the salary figure

    Bolds the FIRST occurrence of each target within each matching paragraph.
    """
    sal     = _salutation(emp)
    name    = emp["name"]
    cnic    = emp["cnic"]
    desig   = emp["designation"]
    dept    = emp["department"]
    salary  = emp.get("salary", "")
    jdate   = emp["joining_date"]

    rules: list[tuple] = [
        # Header — labels only
        (lambda t: t.startswith("Date:") and "Private & Confidential" in t, ["Date:", "CNIC:"]),
        (lambda t: t.startswith("Name:"), ["Name:"]),
        # First paragraph — name only (not the parentheticals), plus key identifiers
        (lambda t: "is pleased to offer" in t,
         [f"{sal} {name}", desig, f"{dept} Team", f"{dept} Department", "Orenda", jdate]),
        # Offer acceptance — name + CNIC
        (lambda t: t.lstrip().startswith("I,") and "CNIC" in t, [name, cnic]),
        # Compensation — salary figure
        (lambda t: ("Gross Salary" in t) or ("PKR" in t and "/month" in t),
         [f"PKR {salary}"] if salary else []),
    ]

    doc = docs.documents().get(documentId=doc_id).execute()
    requests: list[dict] = []

    def handle(elements):
        for el in elements:
            if "paragraph" in el:
                runs = [pe for pe in el["paragraph"].get("elements", []) if "textRun" in pe]
                if runs:
                    base = runs[0].get("startIndex", 0)
                    full = "".join(pe["textRun"].get("content", "") for pe in runs)
                    for pred, subs in rules:
                        if pred(full):
                            # Clear any inherited bold across the whole paragraph first,
                            # then bold ONLY the intended substrings.
                            end = runs[-1].get("endIndex", base + len(full))
                            requests.append({"updateTextStyle": {
                                "range": {"startIndex": base, "endIndex": end},
                                "textStyle": {"bold": False},
                                "fields": "bold",
                            }})
                            for sub in subs:
                                if not sub or len(sub) < 2:
                                    continue
                                i = full.find(sub)
                                if i != -1:
                                    requests.append({"updateTextStyle": {
                                        "range": {"startIndex": base + i, "endIndex": base + i + len(sub)},
                                        "textStyle": {"bold": True},
                                        "fields": "bold",
                                    }})
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        handle(cell.get("content", []))

    handle(doc["body"]["content"])
    for i in range(0, len(requests), 50):
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests[i:i+50]}).execute()


# ── Branded footer helper ─────────────────────────────────────────────────────

def _footer_has_logo(doc: dict, footer_id: str) -> bool:
    """True if the footer already contains a logo — either an inline image in the
    footer text, or a positioned object anchored to a footer paragraph (this is how
    the OPL/OWT templates embed their tree logo)."""
    footer = doc.get("footers", {}).get(footer_id, {})
    for el in footer.get("content", []):
        if "paragraph" not in el:
            continue
        if el["paragraph"].get("positionedObjectIds"):
            return True
        for pe in el["paragraph"].get("elements", []):
            if "inlineObjectElement" in pe:
                return True
    return False


def _add_footer(docs: Resource, doc_id: str, address: str = FOOTER_ADDRESS) -> None:
    """Add the standard branded footer to every page: tree logo + centred address line.

    Most templates already embed the tree logo in the footer (as a positioned
    object) — in that case we only add the centred address text so we don't end up
    with two overlapping trees. If a template has no footer logo at all, we insert
    one (reusing the logo embedded elsewhere in the doc). Address is 9pt grey,
    centred.
    """
    doc = docs.documents().get(documentId=doc_id).execute()
    footer_id = doc.get("documentStyle", {}).get("defaultFooterId")

    # Create a default footer if the template doesn't already have one
    if not footer_id:
        reply = docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"createFooter": {"type": "DEFAULT"}}]},
        ).execute()
        footer_id = reply["replies"][0]["createFooter"]["footerId"]
        doc = docs.documents().get(documentId=doc_id).execute()

    has_logo = _footer_has_logo(doc, footer_id)

    # Insert the address text (no tab — the paragraph is centred)
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [
            {"insertText": {"location": {"segmentId": footer_id, "index": 0}, "text": address}}
        ]},
    ).execute()

    # Only add a logo if the footer doesn't already have one
    if not has_logo:
        candidates: list[tuple[str | None, str]] = []
        for objs, prop in (
            (doc.get("positionedObjects", {}), "positionedObjectProperties"),
            (doc.get("inlineObjects", {}),     "inlineObjectProperties"),
        ):
            for _oid, o in objs.items():
                emb = o.get(prop, {}).get("embeddedObject", {})
                uri = emb.get("imageProperties", {}).get("contentUri")
                if uri:
                    candidates.append((emb.get("description"), uri))
        logo_uri = next(
            (uri for desc, uri in candidates if desc and "orenda" in desc.lower()),
            candidates[0][1] if candidates else None,
        )
        if logo_uri:
            docs.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": [{
                    "insertInlineImage": {
                        "location": {"segmentId": footer_id, "index": 0},
                        "uri": logo_uri,
                        "objectSize": {
                            "height": {"magnitude": 22, "unit": "PT"},
                            "width":  {"magnitude": 17, "unit": "PT"},
                        },
                    }
                }]},
            ).execute()

    # Centre the footer paragraph and style the address: 9pt, grey
    doc = docs.documents().get(documentId=doc_id).execute()
    footer = doc["footers"][footer_id]
    para_start = text_start = text_end = None
    for el in footer["content"]:
        if "paragraph" not in el:
            continue
        if para_start is None:
            para_start = el.get("startIndex", 0)
        for pe in el["paragraph"].get("elements", []):
            tr = pe.get("textRun")
            if tr and tr["content"].strip():
                if text_start is None:
                    text_start = pe.get("startIndex", 0)
                text_end = pe.get("endIndex")

    requests: list[dict] = [{
        "updateParagraphStyle": {
            "range": {"segmentId": footer_id, "startIndex": para_start, "endIndex": (text_end or para_start + 1)},
            "paragraphStyle": {"alignment": "CENTER"},
            "fields": "alignment",
        }
    }]
    if text_start is not None:
        requests.append({
            "updateTextStyle": {
                "range": {"segmentId": footer_id, "startIndex": text_start, "endIndex": text_end},
                "textStyle": {
                    "fontSize": {"magnitude": 9, "unit": "PT"},
                    "foregroundColor": {"color": {"rgbColor": {"red": 0.5, "green": 0.5, "blue": 0.5}}},
                },
                "fields": "fontSize,foregroundColor",
            }
        })
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()


# ── JD extraction helpers ─────────────────────────────────────────────────────

_JD_SECTIONS = {"Key Responsibilities"}


def _extract_jd_lines(docs: Resource, jd_doc_id: str) -> list[tuple[str, bool]]:
    """Read a JD Google Doc under 'Key Responsibilities'; return clean (text, is_heading) items."""
    doc = docs.documents().get(documentId=jd_doc_id).execute()
    items: list[tuple[str, bool]] = []
    in_section = False

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
            elif in_section and style == "HEADING_3":
                items.append((f"{text}:", True))
            elif in_section and style == "HEADING_2":
                # New top-level section — stop extracting
                in_section = False
        elif in_section and el["paragraph"].get("bullet"):
            items.append((f"\u2022 {text}", False))

    return items


def _jd_text_to_items(raw: str) -> list[tuple[str, bool]]:
    """Convert pasted/Markaz JD text into (text, is_heading) items for Annexure-A.

    - blank lines are dropped
    - a short line ending with ':' is treated as a bold sub-heading
    - everything else becomes a bullet (existing bullet glyphs/dashes are normalised)
    """
    items: list[tuple[str, bool]] = []
    for line in raw.splitlines():
        t = line.strip()
        if not t:
            continue
        stripped = t.lstrip("•-*• ").strip()
        if not stripped:
            continue
        if stripped.endswith(":") and len(stripped) <= 70:
            items.append((stripped, True))            # sub-heading → bold
        else:
            items.append((f"• {stripped}", False))  # bullet
    return items


def _insert_jd_into_annexure(docs: Resource, contract_id: str, jd_items: list[tuple[str, bool]]) -> None:
    """Insert JD items after the 'Key Responsibilities' heading — clean spacing
    (one line per item, NO blank lines) and bold the heading + every sub-heading."""
    if not jd_items:
        return
    doc = docs.documents().get(documentId=contract_id).execute()
    kr_idx = jd_idx = None
    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        ).strip()
        # Match flexibly: some templates combine it as "Job Description: Key Responsibilities:"
        if "Key Responsibilities" in text and kr_idx is None:
            kr_idx = el["endIndex"]
        elif text.startswith("Job Description") and jd_idx is None:
            jd_idx = el["endIndex"]
    # Prefer inserting right after "Key Responsibilities"; fall back to "Job Description"
    insert_idx = kr_idx if kr_idx is not None else jd_idx
    if insert_idx is None:
        return

    # Clean insert: one line per item, no extra blank lines, no leading newline
    jd_text = "\n".join(text for text, _ in jd_items) + "\n"
    docs.documents().batchUpdate(
        documentId=contract_id,
        body={"requests": [{"insertText": {"location": {"index": insert_idx}, "text": jd_text}}]},
    ).execute()

    # Bold the "Key Responsibilities" heading and each sub-heading line
    headings = {"Key Responsibilities"} | {text for text, is_h in jd_items if is_h}
    doc = docs.documents().get(documentId=contract_id).execute()
    requests: list[dict] = []

    def walk(elements):
        for el in elements:
            if "paragraph" in el:
                runs = [pe for pe in el["paragraph"].get("elements", []) if "textRun" in pe]
                if runs:
                    full = "".join(pe["textRun"].get("content", "") for pe in runs)
                    if full.strip() in headings:
                        base = runs[0].get("startIndex", 0)
                        length = len(full.rstrip("\n"))
                        requests.append({"updateTextStyle": {
                            "range": {"startIndex": base, "endIndex": base + length},
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }})
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        walk(cell.get("content", []))

    walk(doc["body"]["content"])
    for i in range(0, len(requests), 50):
        docs.documents().batchUpdate(documentId=contract_id, body={"requests": requests[i:i+50]}).execute()


def _fill_header_date(docs: Resource, contract_id: str, date_str: str) -> None:
    """Insert the date into the blank date cell in the contract header.
    The value is left UN-bold — only the 'Date:' label is bold (see _bold_contract)."""
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


def _fill_hod_block(docs: Resource, contract_id: str, name: str, designation: str, date_str: str) -> None:
    """Fill the HoD signing block: name + designation via labels, and the standalone
    'Date' line surgically (so 'Commencement Date' / 'Offer Acceptance Date' are untouched)."""
    pairs: list[tuple[str, str]] = []
    if name:
        pairs.append(("Head of Department's Name", name))
        pairs.append(("HOD Name", name))
    if designation:
        pairs.append(("Designation", designation))
    if pairs:
        _apply_replacements(docs, contract_id, pairs)

    # Surgically replace the standalone "Date" paragraph (the HoD date line)
    doc = docs.documents().get(documentId=contract_id).execute()
    target = {"idx": None}

    def find(elements):
        for el in elements:
            if target["idx"] is not None:
                return
            if "paragraph" in el:
                runs = el["paragraph"].get("elements", [])
                t = "".join(pe.get("textRun", {}).get("content", "") for pe in runs).strip()
                if t == "Date":
                    for pe in runs:
                        if pe.get("textRun", {}).get("content", "").strip() == "Date":
                            target["idx"] = pe.get("startIndex")
                            return
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        find(cell.get("content", []))

    find(doc["body"]["content"])
    if target["idx"] is not None:
        i = target["idx"]
        docs.documents().batchUpdate(
            documentId=contract_id,
            body={"requests": [
                {"deleteContentRange": {"range": {"startIndex": i, "endIndex": i + 4}}},
                {"insertText": {"location": {"index": i}, "text": date_str}},
            ]},
        ).execute()


def _remove_probation_clause(docs: Resource, contract_id: str) -> None:
    """Remove the Probation heading + clause (used for internal transitions).
    Deletes everything from the 'Probation' heading up to the next 'Compensation' heading."""
    doc = docs.documents().get(documentId=contract_id).execute()
    content = doc["body"]["content"]
    start_idx = end_idx = None
    for i, el in enumerate(content):
        if "paragraph" not in el:
            continue
        t = "".join(pe.get("textRun", {}).get("content", "") for pe in el["paragraph"].get("elements", [])).strip()
        if t == "Probation":
            start_idx = el["startIndex"]
            for el2 in content[i + 1:]:
                if "paragraph" not in el2:
                    continue
                t2 = "".join(pe.get("textRun", {}).get("content", "") for pe in el2["paragraph"].get("elements", [])).strip()
                if t2 == "Compensation":
                    end_idx = el2["startIndex"]
                    break
            break
    if start_idx is not None and end_idx is not None and end_idx > start_idx:
        docs.documents().batchUpdate(
            documentId=contract_id,
            body={"requests": [{"deleteContentRange": {"range": {"startIndex": start_idx, "endIndex": end_idx}}}]},
        ).execute()


def _insert_page_breaks(docs: Resource, contract_id: str) -> None:
    """Start the Offer Acceptance section and the Annexure-A (Job Description) on new pages."""
    for marker in ("Annexure- A", "OFFER ACCEPTANCE:"):   # fresh fetch each time → order-independent
        doc = docs.documents().get(documentId=contract_id).execute()
        found = {"idx": None}

        def find(elements):
            for el in elements:
                if found["idx"] is not None:
                    return
                if "paragraph" in el:
                    t = "".join(pe.get("textRun", {}).get("content", "") for pe in el["paragraph"].get("elements", [])).strip()
                    if t == marker or (marker.startswith("Annexure") and t.startswith("Annexure")):
                        found["idx"] = el.get("startIndex")
                        return
                elif "table" in el:
                    for row in el["table"].get("tableRows", []):
                        for cell in row.get("tableCells", []):
                            find(cell.get("content", []))

        find(doc["body"]["content"])
        if found["idx"]:
            docs.documents().batchUpdate(
                documentId=contract_id,
                body={"requests": [{"insertPageBreak": {"location": {"index": found["idx"]}}}]},
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


# ── Date format helpers ───────────────────────────────────────────────────────

def _ordinal(n: int) -> str:
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _day_of(s: str) -> str:
    """'1 July 2026' → '1st day of July, 2026' (the project-contract term format)."""
    for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s.strip(), fmt)
            return f"{_ordinal(d.day)} day of {d.strftime('%B')}, {d.year}"
        except (ValueError, AttributeError):
            continue
    return s  # leave as-is if it doesn't parse


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
    hod_name     = emp.get("hod_name", "")
    hod_desig    = emp.get("hod_designation", "")
    direct_rep   = emp.get("direct_report", "")
    indirect_rep = emp.get("indirect_report", "")

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
                # Standard: first paragraph says only "Orenda" (not the full legal name)
                f"position of {designation} as part of the {department} Team of Orenda",
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
        # Salary breakdown — standard Orenda split: Base = Gross×90%, Medical = Base×10%, Others = remainder.
        try:
            gross = float(str(salary).replace(",", "").replace("PKR", "").strip())
        except ValueError:
            gross = 0.0
        base = round(gross * 0.90)
        medical = round(base * 0.10)
        others = round(gross - base - medical)
        money = lambda n: f"{int(n):,}"
        return [
            ("Current Date",                             today),
            # Header block — template uses a curly apostrophe (’), not a straight one
            ("EMPLOYEE’S CNIC",                          cnic),
            ("EMPLOYEE’S NAME",                          name),
            ("EFFECTIVE DATE OF JOINING",                joining_date),
            # Parties paragraph: "Mr./Mrs. EMPLOYEE NAME bearing CNIC No: X Y Z"
            ("Mr./Mrs.",                                 sal),
            ("EMPLOYEE NAME",                            name),
            ("X Y Z",                                    cnic),
            # Term dates — "Xth day of Month, Year" format
            ("DATE, MONTH, YEAR to DATE, MONTH , YEAR",  f"{_day_of(start_date)} to {_day_of(end_date)}"),
            # Designation (table label; value cell is blank → append after the colon)
            ("Designation:",                             f"Designation: {designation}"),
            # Duration (template has two spaces before XYZ)
            ("with a duration of  XYZ",                  f"with a duration of {duration}"),
            # Compensation breakdown
            ("Total Earnings PKR XYZ Per month inclusive of Tax",
             f"Total Earnings PKR {salary} Per month inclusive of Tax"),
            ("Base Salary: PKR XYZ",                     f"Base Salary: PKR {money(base)}"),
            ("Medical: PKR XYZ",                         f"Medical: PKR {money(medical)}"),
            ("Others: PKR XYZ",                          f"Others: PKR {money(others)}"),
            # Offer-acceptance line: "I, NAME, bearing CNIC # XYZ … will join Orenda XYZ (joining date)."
            ("bearing CNIC # XYZ",                       f"bearing CNIC # {cnic}"),
            ("join Orenda XYZ (joining date)",           f"join Orenda on {joining_date}"),
            # Employer signatory = Head of Department (entered in the form)
            ("EMPLOYER NAME DESIGNATION",                f"{hod_name}\n{hod_desig}"),
            # Reporting lines (manual entry for project contracts)
            ("Direct Report to: ",                       f"Direct Report to: {direct_rep}"),
            ("Coordination & Indirect Report to: ",      f"Coordination & Indirect Report to: {indirect_rep}"),
            # NOTE: leave policy is fixed legal text — updated directly in the template
            # (single "Unlimited trust-based leaves" clause), not patched here.
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
                hod_name        HoD / signatory name (ALWAYS ask if not provided)
                hod_designation HoD / signatory designation
                jd_doc_id       Google Doc ID of the Job Description (fills Annexure A)
                is_transition   True for internal transitions → omits the probation clause

    entity:          "owt" | "opl" | "taleemabad" | "orenda"
    employment_type: "full_time" | "project" | "part_time" | "addendum"

    Formatting follows the locked standards in skills/3-document-drafting.md:
    header labels bold (not values), first-paragraph name-only bold + "Orenda",
    offer-acceptance name+CNIC bold, page breaks before Offer Acceptance & Annexure-A,
    clean JD spacing with bold headings, branded footer.
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

    # NDA bolding values — name + dates (contract is bolded separately by _bold_contract)
    nda_bold_values = [
        v for k in ("cnic", "joining_date") if (v := emp.get(k, "")) and len(v) > 2
    ]
    nda_bold_values.append(emp["name"])

    # 1. Ensure parent folder
    parent_id = _get_or_create_parent_folder(drive)

    # 2. Employee sub-folder
    emp_folder_id = _create_employee_folder(drive, parent_id, emp)
    print(f"  Created folder: {emp['name']} - {emp['joining_date']}")

    today_str = datetime.now().strftime("%d %B %Y")

    # 3. Contract: copy → fill placeholders → remove highlights
    contract_title = f"{emp['name']} - Contract"
    contract_id = _copy_template(drive, TEMPLATE_IDS[contract_key], contract_title, emp_folder_id)
    _apply_replacements(docs, contract_id, _replacements(contract_key, emp))
    _remove_highlights(docs, contract_id)

    # 3a. Header date (value left un-bold — only the label is bold)
    _fill_header_date(docs, contract_id, today_str)

    # 3b. Offer acceptance placeholders (NAME / CNIC)
    _fill_offer_acceptance(docs, contract_id, emp["name"], emp["cnic"])

    # 3c. HoD signing block (name + designation + today's date, surgical).
    #     Skip for opl_project — it fills its signatory via the "EMPLOYER NAME DESIGNATION"
    #     token; the generic bare-"Designation" replacement would corrupt its table label.
    hod_name = emp.get("hod_name", "")
    hod_designation = emp.get("hod_designation", "")
    if (hod_name or hod_designation) and contract_key != "opl_project":
        _fill_hod_block(docs, contract_id, hod_name, hod_designation, today_str)

    # 3d. Internal transition → remove the probation clause
    if emp.get("is_transition"):
        _remove_probation_clause(docs, contract_id)
        print("  Removed probation clause (internal transition)")

    # 3e. Insert JD into Annexure A (clean spacing, bold headings).
    #     Source priority: a JD Google Doc link (structured), else pasted/Markaz JD text.
    jd_doc_id = emp.get("jd_doc_id", "")
    jd_text = emp.get("jd_text", "")
    jd_items: list[tuple[str, bool]] = []
    if jd_doc_id:
        jd_items = _extract_jd_lines(docs, jd_doc_id)
    if not jd_items and jd_text:
        jd_items = _jd_text_to_items(jd_text)
    if jd_items:
        _insert_jd_into_annexure(docs, contract_id, jd_items)
        print(f"  Inserted JD ({len(jd_items)} items) into Annexure A")

    # 3f. Page breaks: Offer Acceptance + Annexure-A each start on a new page.
    #     opl_project already uses section breaks for this — inserting page breaks there
    #     would double up and leave a blank page, so skip it.
    if contract_key != "opl_project":
        _insert_page_breaks(docs, contract_id)

    # 3g. Bold contract fields per standards (segment-aware)
    _bold_contract(docs, contract_id, emp)

    # 3h. Branded footer (logo + centred address) on every page
    _add_footer(docs, contract_id)
    print("  Added branded footer")

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
        _bold_fields(docs, nda_id, nda_bold_values)
        print(f"  Drafted NDA:       {nda_title}")
        audit_log("NDA_CREATED", f"employee='{emp['name']}' doc_id={nda_id}")
        nda_url = f"https://docs.google.com/document/d/{nda_id}/edit"

    return {
        "employee":     emp["name"],
        "folder_url":   f"https://drive.google.com/drive/folders/{emp_folder_id}",
        "contract_url": f"https://docs.google.com/document/d/{contract_id}/edit",
        "nda_url":      nda_url,
    }
