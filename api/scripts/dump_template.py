"""Dump a contract template's paragraph text so we can see its exact placeholder tokens."""
import sys
from hr_assistant.config import get_google_services
from hr_assistant.contract_service import TEMPLATE_IDS

key = sys.argv[1] if len(sys.argv) > 1 else "opl_project"
docs = get_google_services(allow_interactive=False)["docs"]
doc = docs.documents().get(documentId=TEMPLATE_IDS[key]).execute()

print(f"=== TEMPLATE: {key} ({doc.get('title')}) ===\n")


def walk(elements, depth=0):
    for el in elements:
        if "paragraph" in el:
            txt = "".join(pe.get("textRun", {}).get("content", "")
                          for pe in el["paragraph"].get("elements", []))
            t = txt.rstrip("\n")
            if t.strip():
                print(("  " * depth) + repr(t))
        elif "table" in el:
            print(("  " * depth) + "[TABLE]")
            for row in el["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    walk(cell.get("content", []), depth + 1)


walk(doc["body"]["content"])
