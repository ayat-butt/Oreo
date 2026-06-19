# Archive — Legacy Scripts and Analysis

This folder contains old development, debugging, and analysis scripts from previous project iterations. These are **not** part of the active project flow.

## Contents

### `/old_scripts/` (138 Python files)
Legacy development scripts including:
- **Debugging scripts:** `check_*.py`, `verify_*.py`, `debug_*.py`
- **Data extraction:** `extract_*.py`, `analyze_*.py`
- **Sheet operations:** `create_*.py`, `update_*.py`, `add_*.py`
- **Geocoding/coordinates:** `geocode_*.py`, `*coordinates*.py` (old project)
- **Insurance workflows:** `*insurance*.py` (old project)
- **Probation/hierarchy:** `*hierarchy*.py`, `*org_*.py` (old project)
- **Tax/payroll analysis:** `*tax*.py`, `*payroll*.py` (superseded by payroll/ folder)

These were used for one-off investigations, iterations, and debugging. Not needed for current operations.

### `/old_analysis/` (CSV, JSON, TXT files)
Legacy analysis reports and data extracts:
- **Tax verification reports** (April 2026, March 2026)
- **Documentation audits**
- **Data extraction outputs** (markaz, coordinates, etc.)
- **Intermediate processing files**

## When to Use Archive

- **DO archive scripts if:** Debugging complete, iteration finished, one-off analysis done, or workflow replaced
- **DO NOT archive if:** Script is part of active workflow or monthly process

## How to Restore

```bash
# If you need a script from archive:
mv archive/old_scripts/script_name.py ./
```

---
**Last cleanup:** 2026-05-12  
**Archived:** 140+ files, 1.5 MB freed
