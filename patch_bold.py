"""
One-off script: apply the two missing bold fixes to the existing Ayat Butt contract.
Bolds: "People and Culture Team", "Orenda Private Limited", "Ayat Butt", "CNIC 82203-9314104-6"
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from hr_assistant.config import get_google_services
from hr_assistant.contract_service import _bold_fields

CONTRACT_ID = "1cjemT8_lgADZIGhjvsNVROWHPuTbHOuZY6icVkZK2h8"

BOLD_TARGETS = [
    "People and Culture Team",
    "Orenda Private Limited",
    "Ayat Butt",
    "82203-9314104-6",   # CNIC value in offer acceptance
]

def main():
    services = get_google_services()
    docs = services["docs"]
    print("Applying bold fixes to Ayat Butt contract...")
    _bold_fields(docs, CONTRACT_ID, BOLD_TARGETS)
    print("Done. Open the contract to verify:")
    print(f"  https://docs.google.com/document/d/{CONTRACT_ID}/edit")

if __name__ == "__main__":
    main()
