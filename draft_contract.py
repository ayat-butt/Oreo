"""
Draft a contract + NDA for a new hire, then create the welcome email draft.

Usage:
    python draft_contract.py

Fill in the employee details below, run the script, then:
  1. Review the Google Docs links (Contract + NDA)
  2. Review the Gmail draft in your Drafts folder
  3. Send the email manually once you're happy with both
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services
from hr_assistant.contract_service import draft_contracts
from hr_assistant.email_service import draft_welcome_email

# ── Fill in employee details here ─────────────────────────────────────────────
EMPLOYEE = {
    # Required for all contract types
    "name":             "Full CNIC Name Here",        # e.g. "Muhammad Ali Khan"
    "cnic":             "XXXXX-XXXXXXX-X",            # e.g. "42101-1234567-9"
    "designation":      "Designation Here",           # e.g. "Software Engineer"
    "department":       "Department Here",            # e.g. "Technology"
    "salary":           "XX,XXX",                     # e.g. "85,000"
    "joining_date":     "DD Month YYYY",              # e.g. "01 April 2026"

    # Entity: "owt" | "opl" | "taleemabad" | "orenda"
    "entity":           "opl",

    # Employment type: "full_time" | "project" | "part_time" | "addendum"
    "employment_type":  "full_time",

    # Required only for project / part_time contracts
    # "start_date":     "01 April 2026",
    # "end_date":       "30 June 2026",
    # "duration":       "3",              # in months

    # Required only for addendum
    # "prev_contract_date": "01 January 2026",

    # Optional: Head of Department (fills signing section)
    # "hod_name":           "Waqas Tanveer",
    # "hod_designation":    "Head of Growth",

    # Optional: Job Description Google Doc ID (fills Annexure A with key responsibilities)
    # "jd_doc_id":          "1BjSeezX38b35wIUCtyFhHMZlt-jSHNGVV8jVAaCTCc0",

    # Required for welcome email draft
    "email":            "candidate@email.com",          # candidate's personal email
}
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print("Connecting to Google services...")
    services = get_google_services()
    drive = services["drive"]
    docs  = services["docs"]
    gmail = services["gmail"]

    print(f"\nDrafting contracts for: {EMPLOYEE['name']}")
    print(f"Entity: {EMPLOYEE['entity'].upper()}  |  Type: {EMPLOYEE['employment_type']}\n")

    # Step 1 — Draft contracts in Google Drive
    result = draft_contracts(drive, docs, EMPLOYEE)

    # Step 2 — Create welcome email draft with PDFs attached
    print("\nCreating welcome email draft...")
    # Extract doc IDs from the result URLs
    contract_id = result["contract_url"].split("/d/")[1].split("/")[0]
    nda_id      = result["nda_url"].split("/d/")[1].split("/")[0] if result["nda_url"] else None
    email_result = draft_welcome_email(drive, gmail, EMPLOYEE, contract_id, nda_id)

    print("\n" + "=" * 60)
    print("REVIEW BEFORE SENDING")
    print("=" * 60)
    print(f"Employee folder : {result['folder_url']}")
    print(f"Contract        : {result['contract_url']}")
    if result["nda_url"]:
        print(f"NDA             : {result['nda_url']}")
    print(f"\nGmail draft     : '{email_result['subject']}' → {email_result['to']}")
    print("=" * 60)
    print("\n1. Open the links above and verify the contract + NDA.")
    print("2. Open Gmail Drafts, review the email and attached PDFs.")
    print("3. Send the email manually once you're satisfied.")


if __name__ == "__main__":
    main()
