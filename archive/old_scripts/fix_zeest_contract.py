"""
One-time fix for Zeest Hassan Qureshi's OPL Full Time contract.

Applies 3 remaining corrections:
  1. Date header: insert "27 March 2026" into the blank date cell
  2. Offer acceptance: replace NAME → Zeest Hassan Qureshi, CNIC XYZ → 42201-5176800-9
  3. Insert JD key responsibilities as bullet points in Annexure A
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

CONTRACT_ID   = "1GyBVX--SIrTCZK-ABn_954YLlISWDXl40OEOFS0VxG0"
JD_DOC_ID     = "1BjSeezX38b35wIUCtyFhHMZlt-jSHNGVV8jVAaCTCc0"
EMPLOYEE_NAME = "Zeest Hassan Qureshi"
EMPLOYEE_CNIC = "42201-5176800-9"
SIGN_DATE     = "27 March 2026"

# Sections to extract from the JD doc
JD_SECTIONS = {
    "Key Responsibilities",
    "Required Qualifications & Experience",
    "Critical Competencies",
    "Non-Negotiable Requirements",
    "Success Metrics (First 6 Months)",
}


def _batch_update(docs, doc_id, requests):
    result = docs.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()
    return result


def _get_doc(docs, doc_id):
    return docs.documents().get(documentId=doc_id).execute()


def _extract_jd_content(docs, jd_doc_id: str) -> list[str]:
    """
    Extract all bullet points from Key Responsibilities section and onwards
    (through Success Metrics). Returns clean bullet strings (no leading bullet char).
    """
    doc = _get_doc(docs, jd_doc_id)
    lines = []
    in_section = False
    current_heading = None

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
            if text in JD_SECTIONS:
                in_section = True
                current_heading = text
                lines.append(f"\n{text}")  # section heading as bold line
            elif any(text.startswith(s) for s in JD_SECTIONS) or (
                in_section and style == "HEADING_3"
            ):
                # sub-heading within an active section
                if in_section:
                    lines.append(f"\n{text}:")
            else:
                # new unrelated heading — stop if we were past Success Metrics
                if current_heading == "Success Metrics (First 6 Months)":
                    in_section = False
        elif in_section:
            # Normal text bullet items
            is_bullet = bool(el["paragraph"].get("bullet"))
            if is_bullet:
                lines.append(f"• {text}")
            # skip non-bullet prose in sections

    return [l for l in lines if l.strip()]


def main():
    print("Connecting to Google services...")
    services = get_google_services()
    docs = services["docs"]

    # ── Step 1: replaceAllText fixes ─────────────────────────────────────────
    print("\n[1/3] Replacing offer acceptance placeholders...")
    r1 = _batch_update(docs, CONTRACT_ID, [
        {
            "replaceAllText": {
                "containsText": {"text": "I, NAME , the employee, bearing CNIC XYZ",
                                 "matchCase": True},
                "replaceText": f"I, {EMPLOYEE_NAME} , the employee, bearing CNIC {EMPLOYEE_CNIC}",
            }
        },
    ])
    for reply in r1.get("replies", []):
        n = reply.get("replaceAllText", {}).get("occurrencesChanged", 0)
        print(f"  replaced {n} occurrence(s)")

    # ── Step 2: Insert date into header (index-based) ─────────────────────────
    # We confirmed the date line is paragraph [99-151]: "Date: \tPrivate & ..."
    # The date value should go right after "Date: " (6 chars from index 99 = 105)
    print("\n[2/3] Inserting date into header...")
    # Re-read to confirm index hasn't shifted (replaceAllText may have shifted it)
    doc = _get_doc(docs, CONTRACT_ID)
    date_insert_idx = None
    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        si = el.get("startIndex", 0)
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        )
        if text.startswith("Date: ") and "Private & Confidential" in text:
            # Check the date value field is blank (still "Date: \t...")
            after_label = text[6:]  # everything after "Date: "
            if after_label.startswith("\t") or after_label.startswith("P"):
                # Date value is blank (tab immediately after label)
                date_insert_idx = si + 6  # insert after "Date: "
                print(f"  Found date paragraph at index {si}, inserting at {date_insert_idx}")
            else:
                print(f"  Date already filled: {after_label[:40]!r}")
            break

    if date_insert_idx is not None:
        _batch_update(docs, CONTRACT_ID, [
            {
                "insertText": {
                    "location": {"index": date_insert_idx},
                    "text": SIGN_DATE,
                }
            }
        ])
        print(f"  Inserted '{SIGN_DATE}' at index {date_insert_idx}")
    else:
        print("  Date paragraph not found or already filled.")

    # ── Step 3: Insert JD bullets into Annexure A ────────────────────────────
    print("\n[3/3] Extracting JD and inserting into Annexure A...")
    jd_lines = _extract_jd_content(docs, JD_DOC_ID)
    print(f"  Extracted {len(jd_lines)} lines from JD doc.")
    if not jd_lines:
        print("  WARNING: No JD content found.")
        return

    print("  Preview (first 8):")
    for l in jd_lines[:8]:
        print(f"    {l}")

    # Re-read contract to get current Annexure A index (may have shifted)
    doc = _get_doc(docs, CONTRACT_ID)
    annexure_insert_idx = None
    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        ).strip()
        if text in ("Key Responsibilities", "Key Responsibilities:"):
            annexure_insert_idx = el["endIndex"]
            print(f"  Found 'Key Responsibilities' heading, inserting at {annexure_insert_idx}")
            break

    if annexure_insert_idx is None:
        print("  WARNING: Could not find 'Key Responsibilities' in Annexure A.")
        return

    jd_text = "\n".join(jd_lines) + "\n"
    _batch_update(docs, CONTRACT_ID, [
        {
            "insertText": {
                "location": {"index": annexure_insert_idx},
                "text": "\n" + jd_text,
            }
        }
    ])
    print(f"  Inserted {len(jd_lines)} lines of JD content.")

    print("\nDone. Review the contract:")
    print(f"  https://docs.google.com/document/d/{CONTRACT_ID}/edit")


if __name__ == "__main__":
    main()
