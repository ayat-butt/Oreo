# Google Sheets Operations — fetch_sheets_data.py

## Overview

**Script:** `fetch_sheets_data.py` (PRIMARY method for all sheet access)  
**Method:** Direct Google Sheets API v4 (not MCP wrappers)  
**Authentication:** Uses local token.json  
**Status:** ✅ Verified working (colleague-validated approach)

## When to Use

- Read any Google Sheet
- Count rows/employees
- Fetch specific data ranges
- Verify sheet structure
- Spot-check suspicious data

## How It Works

The script follows 7 steps:

1. **Load credentials** — Read token.json
2. **Build Sheets API client** — Create v4 service
3. **Fetch metadata** — Get all tab/sheet names
4. **Read headers** — Understand column structure
5. **Read sample rows** — Check format (typically rows 1-5)
6. **Count data** — Tally non-empty rows per entity
7. **Verify sparse data** — Deep-check if counts seem low

## Usage

```bash
# Basic: Fetch data from a spreadsheet
cd c:\Agent Oreo
python fetch_sheets_data.py

# To modify for a specific sheet:
# Edit the spreadsheet_id variable in the script
```

## Script Location

📄 `c:\Agent Oreo\fetch_sheets_data.py`

## Output

The script prints:
- All tab names found
- Column headers
- Sample data (first 5 rows)
- Employee/row counts per tab
- Full data for sparse tabs (≤5 rows)

## Example Output

```
Found 5 tabs:
  1. NIETE_Islamabad
  2. OPL
  3. OWT
  4. NIETE_Balochistan
  5. Taleemabad_Inc_

Processing tab: NIETE_Islamabad
Headers: ['Employee ID', 'Employee Name', 'Job Title', ...]
Employee count: 83
```

## What NOT to Do

❌ Use MCP Google Drive read_file_content()  
❌ Try to read sheets as generic files  
❌ Attempt modifications (read-only for this script)

## To Modify Sheet Data

Use hr_assistant/drive_service.py instead:
```python
from hr_assistant.drive_service import update_sheet_values
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Requested entity not found" | Check spreadsheet ID is correct |
| Token expired | Delete token.json, re-authenticate |
| Permission denied | Verify sheet is shared with zeshan.dhillon@taleemabad.com |
| No tabs found | Spreadsheet may be empty or inaccessible |

---

**Decision:** Primary approach for all sheet reads  
**Verified by:** Colleague (2026-05-12)  
**See also:** [hr_assistant/drive_service.py](../hr_assistant/drive_service.py) for write operations
