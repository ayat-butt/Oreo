---
name: salary-docs
description: Generates Taleemabad employee Salary Ledgers (multi-month, A4 landscape PDF) and Salary Slips (single-month, A4 portrait PDF), then emails them to the employee. Invoked with /salary-ledger, /salary-slip, or /payroll-docs.
triggers:
  - /salary-ledger
  - /salary-slip
  - /payroll-docs
---

# Salary Documents Skill
**Last updated: 2026-04-07**

Generates two types of payroll PDFs for Taleemabad employees:
- **Salary Ledger** – multi-month history, A4 landscape, all compensation columns, colour-coded
- **Salary Slip** – single month, A4 portrait, clean earnings/deductions layout

Both are built with ReportLab (Python), sent via the Umeed Gmail alias.

---

## Files & Scripts

| File | Purpose |
|------|---------|
| `~/umeed/build_salary_ledger.py` | Canonical ledger build script (v14) |
| `~/umeed/build_salary_slip.py` | Canonical slip build script (v1) |
| `~/umeed/gmail_client.py` | Email sender (always use this, never MCP Gmail) |
| `~/umeed/integrations/google_auth.py` | Google OAuth for Sheets API |
| `~/.claude/skills/salary-docs/PAYROLL_REGISTRY.md` | **Payroll sheet IDs by month** – update this monthly |

---

## Environment & Credentials

All secrets live in `~/umeed/.env`:

| Variable | Used For |
|----------|---------|
| `MARKAZ_DATABASE_URL` | Neon PostgreSQL – employee info (name, ID, CNIC, joining date) |
| `GOOGLE_OAUTH_TOKEN` / `google-workspace-token.json` | Google Sheets API read access |
| `ANTHROPIC_API_KEY` | Not needed for doc generation; used for scoring in other skills |

Google auth: `~/umeed/google-workspace-token.json` – loaded via `~/umeed/integrations/google_auth.py`.

---

## Integration Map

```
Markaz HRIS (Neon PostgreSQL)
  ├─ Employee Name, ID, CNIC, Joining Date

Google Sheets API (OAuth)
  ├─ Monthly payroll data (gross, deductions, net, etc.)
  ├─ Sheet IDs from PAYROLL_REGISTRY.md

ReportLab (Python)
  ├─ Builds PDF (ledger or slip)

~/umeed/gmail_client.py
  ├─ Sends PDF as attachment via umeed@taleemabad.com alias
```

---

## Step 1 – Fetch Employee Info (Markaz HRIS)

**Always use HRIS as source of truth for employee metadata. Never hardcode or use sheet data.**

```python
import os, psycopg2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('/Users/zeshanalidhillon/umeed/.env'))
conn = psycopg2.connect(os.getenv('MARKAZ_DATABASE_URL'), connect_timeout=15)
cur = conn.cursor()
cur.execute("""
    SELECT ep.employee_id,
           u.first_name || ' ' || u.last_name AS full_name,
           ep.cnic_number, ep.joining_date,
           ep.official_email, u.email
    FROM employee_profiles ep
    JOIN users u ON ep.user_id = u.id
    WHERE (u.first_name || ' ' || u.last_name) ILIKE %s
""", (f'%{search_name}%',))
row = cur.fetchone()
conn.close()

emp = {
    'name':    row[1],
    'id':      str(row[0]),
    'cnic':    row[2],
    'joining': row[3].strftime('%d %B %Y'),   # e.g. "04 December 2023"
    'email':   row[4] or row[5],              # official_email first, fallback to email
}
```

---

## Step 2 – Fetch Payroll Data (Google Sheets)

Sheet IDs for each month are in [PAYROLL_REGISTRY.md](PAYROLL_REGISTRY.md).

```python
from googleapiclient.discovery import build
from umeed.integrations.google_auth import load_credentials

creds   = load_credentials()
service = build('sheets', 'v4', credentials=creds)

def get_all_tabs(sheet_id):
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    return [s['properties']['title'] for s in meta['sheets']]

def find_employee_in_sheet(sheet_id, emp_id, emp_name):
    """Search ALL tabs. Returns row dict or None."""
    tabs = get_all_tabs(sheet_id)
    SKIP_TABS = {'Sheet1', 'Appraisal Outcome', 'Summary', 'Cover', 'Notes'}
    for tab in tabs:
        if tab in SKIP_TABS:
            continue
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=tab
        ).execute()
        rows = result.get('values', [])
        if not rows:
            continue
        headers = [str(h).strip().lower() for h in rows[0]]
        for row in rows[1:]:
            row_dict = dict(zip(headers, row))
            # Match by ID first, then name
            if emp_id and str(row_dict.get('employee id', '')).strip() == str(emp_id):
                return row_dict
            if emp_name.lower() in str(row_dict.get('employee name', '')).lower():
                return row_dict
    return None
```

### Payroll Field Mapping

Map raw sheet column names – the canonical data dict keys used in PDF generation:

| Canonical Key | Typical Sheet Column Names |
|---------------|---------------------------|
| `gross` | "Gross Salary", "CTC", "Gross Pay" |
| `basic` | "Basic Salary", "Basic Pay" |
| `medical` | "Medical Allowance", "Medical Allow" |
| `other` | "Other Allowance", "Other Allow" |
| `commute` | "Commute Allowance", "Transport Allow", "Fuel Allow" |
| `pending` | "Pending Dues", "Arrears" |
| `overtime` | "Overtime", "OT" |
| `total_allowance` | "Total Allowance", "Gross Amount" |
| `taxable` | "Taxable Salary", "Taxable Income" |
| `income_tax` | "Income Tax", "IT Deduction" |
| `eobi` | "EOBI" |
| `advance` | "Advance", "Salary Advance" |
| `abhi` | "Abhi", "Abhi Advance" |
| `loan` | "Loan", "Loan Deduction" |
| `buscaro` | "BusCaro", "Bus Caro" |
| `lunch` | "Lunch", "Lunch Meal", "Meal Deduction" |
| `unpaid_days` | "Unpaid Days", "Unpaid Leave" |
| `total_deductions` | "Total Deductions" |
| `net` | "Net Salary", "Net Pay", "Net Amount" |

**If a field is absent in the sheet, default to 0 – never crash.**

---

## Step 3A – Build Salary Ledger PDF

The ledger shows all months for one employee on a single A4-landscape page.

```python
# Build the data dict: { "Month Name": { canonical_key: value, ... }, ... }
records = {}
MONTHS = ["July 2025", "August 2025", ..., "February 2026"]  # adjust per request

from PAYROLL_REGISTRY import SHEET_IDS   # or load from PAYROLL_REGISTRY.md manually
for month in MONTHS:
    sheet_id = SHEET_IDS[month]
    raw = find_employee_in_sheet(sheet_id, emp['id'], emp['name'])
    records[month] = map_fields(raw) if raw else {}

# Write /tmp/{name}_full_history.json
import json
with open('/tmp/zeshan_full_history.json', 'w') as f:
    json.dump(records, f)

# Run the canonical build script
import subprocess
subprocess.run(['python3', '/Users/zeshanalidhillon/umeed/build_salary_ledger.py'])
# Output: /tmp/{employee}_salary_ledger_v14.pdf
```

Alternatively, import `build_pdf()` directly from `build_salary_ledger.py` if refactoring for multi-employee batch runs.

### Ledger Layout (top – bottom)

1. **Header** (72pt, #FAFBFD): Orenda logo left · "SALARY LEDGER" centre · Taleemabad logo right · navy + teal rule
2. **Employee Info Block** (58pt, #F4F7FC rounded): Name, ID, CNIC, Joining Date in 2-col · Generated date bottom-right
3. **Colour Legend Band** (16pt, #F0F3FA): Addition (green) + Deduction (red) – two items only
4. **Salary Table** (20 columns, navy header + TOTAL row):

| Column | Style |
|--------|-------|
| Month, Gross, Basic, Medical, Other | Normal |
| Commute, Pending Dues, Overtime | **Green** (Addition) |
| Total Allowance, Taxable, Total Deductions, Net | **Blue-tint** (Summary) |
| Income Tax, EOBI, Advance, Abhi, Loan, BusCaro, Lunch, Unpaid Days | **Red** (Deduction) |

5. **Formula Box** (left, 96pt) + **Signature Block** (right, 200pt) – side by side below table
6. **Footer bar** (navy, 18pt): system-generated notice + hr@taleemabad.com

### Formulas (hardcoded in PDF)
```
Basic Salary        = Gross Salary × 90%
Medical Allow.      = Basic Salary × 10%
Other Allow.        = Gross – Basic – Medical
Total Allowance     = Basic + Medical + Other + Commute + Pending + Overtime
Taxable Salary      = Total Allowance – Medical – Unpaid Days
Total Deductions    = IT + EOBI + Advance + Abhi + Loan + BusCaro + Lunch + Unpaid Days
Net Salary          = Total Allowance – Total Deductions
```

---

## Step 3B – Build Salary Slip PDF

The slip shows one month for one employee, portrait A4.

```python
from umeed.build_salary_slip import build_slip

emp   = { 'name': ..., 'id': ..., 'cnic': ..., 'joining': ..., 'entity': 'OPL' }
data  = records['March 2026']   # single month dict
month = 'March 2026'
out   = f'/tmp/{emp["name"].replace(" ", "_")}_slip_{month.replace(" ", "_")}.pdf'

build_slip(emp, data, month, out)
```

### Slip Layout (top – bottom)

1. **Header** (76pt): Both logos · "SALARY SLIP" · pay period subtitle · navy + teal rule
2. **Employee Info Block** (70pt, rounded): Name, CNIC (left) · Employee ID, Joining Date (right)
3. **Two-column table** – Earnings (green header) | Deductions (red header) – each with alternating rows + total bar
4. **Taxable Salary band** (SUMM_BG #EBF5FB)
5. **Net Salary band** (navy, 50pt) – large PKR figure centred
6. **Signature + HR Queries block** – left: Zeshan's sig + contact; right: hr@taleemabad.com
7. **Footer** (light gray): system-generated notice

---

## Step 4 – Email the Document

**Always use `gmail_client.py`. Never use the MCP Gmail tool for sending payroll docs.**

### Always CC these four addresses on every email:
- `zeshan.dhillon@taleemabad.com`
- `ayat@niete.edu.pk`
- `javariya.mufarrakh@taleemabad.com`
- `salman.iqbal@taleemabad.com`

If the recipient is one of the CC addresses, exclude them from CC to avoid duplicates.

### Salary Ledger Email Template (use verbatim – only substitute placeholders)

**Subject:** `Salary Ledger - [Employee Name] | [Start Month] - [End Month]`

**Body:**
```
Hi [Employee Name],

I hope you are doing well.

Please find attached your Salary Ledger for the period [Month Year] to [Month Year], shared for your review and record.

The document provides a detailed month-wise breakdown of your compensation, including earnings, allowances, applicable deductions, taxable income, and net salary disbursed. This is being shared to ensure transparency and may also be utilized for personal reference, including banking, financial, or tax-related purposes, where required.

Should you identify any discrepancies or require further clarification, please feel free to reach out.

Best Regards,
```

Note: Use ASCII hyphens (`-`) not em dashes (`–`) in the subject line.

### Salary Slip Email Template

**Subject:** `Salary Slip - [Employee Name] | [Month Year]`

**Body (locked – do not modify):**
```
Hi [Employee Name],

Please find attached your salary slips for [Month] - [Year].

Attached PDF is providing a full breakdown of your earnings, deductions, and net pay.

Should you have any questions or identify any discrepancies, please feel free to reach out.

Best Regards,

People & Culture Team
```

### Sending Code
```python
from umeed.gmail_client import GmailClient

client = GmailClient()
client.send_email(
    to=emp['email'],
    subject='Salary Ledger - Zeshan Ali Dhillon | July 2025 - February 2026',
    body=body_text,
    cc='zeshan.dhillon@taleemabad.com,ayat@niete.edu.pk,javariya.mufarrakh@taleemabad.com,salman.iqbal@taleemabad.com',
    attachments=['/tmp/zeshan_salary_ledger_v14.pdf'],
)
```

---

## Design System (colours + assets)

| Token | Hex | Usage |
|-------|-----|-------|
| NAVY | #192D5D | Headers, primary text |
| TEAL | #2CA4AB | Accents, section bars, signature title |
| LIGHT_BG | #F4F7FC | Info block, alt rows |
| MID_GRAY | #8A9BBF | Labels, secondary text |
| DARK_GRAY | #4A5568 | Body data text |
| BORDER | #D0D8EA | Table grid, box outlines |
| GREEN_HL / GREEN_TXT | #E8F5E9 / #1B5E20 | Addition rows |
| RED_HL / RED_TXT | #FFEBEE / #B71C1C | Deduction rows |
| SUMM_BG / SUMM_TXT | #EAF0FB / Navy | Summary rows |

| Asset | Path |
|-------|------|
| Taleemabad logo (transparent PNG) | `~/umeed/assets/taleemabad_logo_transparent.png` |
| Orenda logo | `~/umeed/assets/orenda_logo.png` |
| Zeshan signature | `~/umeed/assets/zeshan_signature.jpg` – remove white bg before embed |

### Signature Background Removal
```python
from PIL import Image as PILImage
import numpy as np

def remove_bg(path):
    img = PILImage.open(path).convert('RGBA')
    arr = np.array(img)
    white = (arr[:,:,0]>200) & (arr[:,:,1]>200) & (arr[:,:,2]>200)
    arr[white, 3] = 0
    return PILImage.fromarray(arr, 'RGBA')
# Always crop tightly to ink bounds before embedding
```

---

## Batch Run (Multiple Employees)

To generate for multiple employees in one pass:

```python
EMPLOYEES = ['Zeshan Ali Dhillon', 'Jawwad Ali', 'Fahad Rao']

for name in EMPLOYEES:
    emp  = fetch_from_hris(name)
    records = fetch_all_months(emp)
    pdf_path = build_ledger(emp, records)
    send_email(emp, pdf_path)
    print(f"Done: {name}")
```

Build all PDFs first, verify them, then send – never send blindly in a loop without spot-checking.

---

## Critical Rules (do not skip)

1. **Tab search**: Always scan ALL tabs in every payroll sheet per employee lookup. Tab names change monthly.
2. **Employee info**: Always fetch from Markaz HRIS. Never pull Name/CNIC/ID from payroll sheets.
3. **CC rule**: Always CC all four addresses (zeshan, ayat, javariya, salman) on every payroll email. Exclude recipient from CC if they're in the list.
4. **Send via gmail_client**: Never use MCP Gmail for sending payroll emails.
5. **Sheet IDs**: Always load from PAYROLL_REGISTRY.md. Never hardcode IDs in scripts.
6. **Zero defaults**: Missing payroll fields – 0. Never crash; build what you have.
7. **Spot check before send**: For batch runs, always open or print the generated PDF to verify layout before emailing.
8. **Joining date format**: `%d %B %Y` – "04 December 2023". It's a datetime from HRIS – always `.strftime()`.

---

## Transferring This Skill to Another Agent

This skill is fully self-contained. To transfer:

1. Copy `~/.claude/skills/salary-docs/` (this folder) to the new agent's skills directory.
2. Ensure the following are available in the new environment:
   - `~/umeed/` directory with all scripts and assets
   - `~/umeed/.env` with `MARKAZ_DATABASE_URL` and Google auth
   - `~/umeed/google-workspace-token.json`
   - Python packages: `reportlab`, `Pillow`, `psycopg2`, `google-api-python-client`, `python-dotenv`, `numpy`
3. Update `PAYROLL_REGISTRY.md` with the latest payroll sheet IDs before first run.
4. Test with one employee (e.g. Zeshan Ali Dhillon) – generate PDF, verify visually, then send.
