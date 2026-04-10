"""
Audit log — every action Oreo takes is recorded here.
Format: YYYY-MM-DD HH:MM:SS | ACTION | DETAILS
"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "oreo_audit.log"


def log(action: str, details: str) -> None:
    """Append one timestamped line to the audit log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | {action} | {details}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"  [AUDIT] {entry.strip()}")
