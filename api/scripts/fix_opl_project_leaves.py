"""One-time template fix: OPL project leave clauses → single 'Unlimited trust-based leaves'.

Deletes the two obsolete leave bullets and rewords the first. Safe: verifies the two
target paragraphs are found and contiguous before deleting; re-dumps the leave area after.
"""
from hr_assistant.config import get_google_services
from hr_assistant.contract_service import TEMPLATE_IDS

docs = get_google_services(allow_interactive=False)["docs"]
DOC = TEMPLATE_IDS["opl_project"]

C36 = ("The Employee is entitled to annual leave of 6 working days for the course of the period "
       "accumulating on a monthly basis, and medical leave of 6 working days.")
C37 = ("Medical Leaves can be availed for a maximum limit of 6 days it will be effective from the "
       "joining date, only for sickness or any other medical purposes.")
C38 = "Only\tunpaid\tleaves\tcan\tbe\tgranted\tif\tthe\tbalance\tis\texhausted."

doc = docs.documents().get(documentId=DOC).execute()
r = {}
for el in doc["body"]["content"]:
    if "paragraph" not in el:
        continue
    text = "".join(pe.get("textRun", {}).get("content", "") for pe in el["paragraph"].get("elements", [])).strip()
    if text == C37:
        r["37"] = (el["startIndex"], el["endIndex"])
    elif text == C38:
        r["38"] = (el["startIndex"], el["endIndex"])

print("found 37:", r.get("37"), "| found 38:", r.get("38"))
if "37" not in r or "38" not in r:
    raise SystemExit("ABORT: could not locate both obsolete clauses — no change made.")
if r["37"][1] != r["38"][0]:
    raise SystemExit(f"ABORT: clauses not contiguous ({r['37']} vs {r['38']}) — no change made.")

# Delete the two obsolete bullets (contiguous range), then reword the first leave clause.
docs.documents().batchUpdate(documentId=DOC, body={"requests": [
    {"deleteContentRange": {"range": {"startIndex": r["37"][0], "endIndex": r["38"][1]}}},
]}).execute()
docs.documents().batchUpdate(documentId=DOC, body={"requests": [
    {"replaceAllText": {"containsText": {"text": C36, "matchCase": True},
                        "replaceText": "The Employee is entitled to Unlimited trust-based leaves."}},
]}).execute()

# verify
doc = docs.documents().get(documentId=DOC).execute()
print("--- leave area now ---")
for el in doc["body"]["content"]:
    if "paragraph" not in el:
        continue
    t = "".join(pe.get("textRun", {}).get("content", "") for pe in el["paragraph"].get("elements", [])).strip()
    if t and ("leave" in t.lower() or "probation" in t.lower() or "unpaid" in t.lower()):
        print("  ", t[:90])
print("done")
