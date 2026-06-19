"""
Second-pass fix for Zeest Hassan Qureshi's contract + NDA.

  1. NDA: replace CURRENT DATE → 27 March 2026 (employer line only)
  2. Contract header: bold the date so it matches Name / CNIC formatting
  3. Contract JD: delete extra sections (Qualifications onwards) — keep only Key Responsibilities
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services

NDA_ID      = "1JXFfJbq3vi89Qlw76vehwe7yTb0MB4sWtbr9gWr3UtY"
CONTRACT_ID = "1GyBVX--SIrTCZK-ABn_954YLlISWDXl40OEOFS0VxG0"
SIGN_DATE   = "27 March 2026"


def _batch(docs, doc_id, requests):
    return docs.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()


def _get(docs, doc_id):
    return docs.documents().get(documentId=doc_id).execute()


# ── 1. NDA: replace CURRENT DATE ──────────────────────────────────────────────
def fix_nda(docs):
    print("[1/3] NDA: replacing CURRENT DATE...")
    result = _batch(docs, NDA_ID, [{
        "replaceAllText": {
            "containsText": {"text": "CURRENT DATE", "matchCase": True},
            "replaceText": SIGN_DATE,
        }
    }])
    n = result["replies"][0].get("replaceAllText", {}).get("occurrencesChanged", 0)
    print(f"  replaced {n} occurrence(s) → '{SIGN_DATE}'")


# ── 2. Contract: bold the header date ─────────────────────────────────────────
def fix_contract_date_bold(docs):
    print("[2/3] Contract: bolding header date...")
    doc = _get(docs, CONTRACT_ID)
    for el in doc["body"]["content"]:
        if "paragraph" not in el:
            continue
        si = el.get("startIndex", 0)
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        )
        if text.startswith("Date: ") and "Private & Confidential" in text:
            # "Date: " is 6 chars; find where the date value ends (before \t)
            date_val = text[6:].split("\t")[0]  # e.g. "27 March 2026"
            if date_val:
                start_bold = si + 6
                end_bold   = si + 6 + len(date_val)
                _batch(docs, CONTRACT_ID, [{
                    "updateTextStyle": {
                        "range": {"startIndex": start_bold, "endIndex": end_bold},
                        "textStyle": {"bold": True},
                        "fields": "bold",
                    }
                }])
                print(f"  bolded '{date_val}' at [{start_bold}-{end_bold}]")
            else:
                print("  date value not found in header paragraph")
            break


# ── 3. Contract: trim JD to Key Responsibilities only ─────────────────────────
def fix_contract_jd(docs):
    print("[3/3] Contract: trimming JD to Key Responsibilities only...")
    doc = _get(docs, CONTRACT_ID)
    content = doc["body"]["content"]

    # Find the startIndex of "Required Qualifications & Experience" paragraph
    qualifications_start = None
    for el in content:
        if "paragraph" not in el:
            continue
        text = "".join(
            pe.get("textRun", {}).get("content", "")
            for pe in el["paragraph"].get("elements", [])
        ).strip()
        if text == "Required Qualifications & Experience":
            qualifications_start = el.get("startIndex")
            print(f"  Found 'Required Qualifications' at index {qualifications_start}")
            break

    if qualifications_start is None:
        print("  'Required Qualifications & Experience' not found — already clean?")
        return

    # Find document end index (last content element's endIndex - 1)
    doc_end = content[-1].get("endIndex", 0) - 1

    # Delete from qualifications_start to doc_end
    # (preserve the very last structural character)
    delete_start = qualifications_start
    delete_end   = doc_end

    if delete_end <= delete_start:
        print("  Nothing to delete.")
        return

    print(f"  Deleting indices [{delete_start}-{delete_end}]...")
    _batch(docs, CONTRACT_ID, [{
        "deleteContentRange": {
            "range": {"startIndex": delete_start, "endIndex": delete_end}
        }
    }])
    print(f"  Done — removed {delete_end - delete_start} characters of extra JD content.")


def main():
    print("Connecting to Google services...")
    services = get_google_services()
    docs = services["docs"]

    fix_nda(docs)
    fix_contract_date_bold(docs)
    fix_contract_jd(docs)

    print("\nAll fixes applied. Review:")
    print(f"  Contract : https://docs.google.com/document/d/{CONTRACT_ID}/edit")
    print(f"  NDA      : https://docs.google.com/document/d/{NDA_ID}/edit")


if __name__ == "__main__":
    main()
