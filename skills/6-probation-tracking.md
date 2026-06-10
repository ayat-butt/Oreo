# Probation Tracker Skill File

> A complete, self-contained guide to keeping the **Probation Tracker** Google Sheet
> accurate and up to date. Anyone — a person or another AI agent — should be able to
> follow this file end-to-end with no other context.

---

## 1. What This Skill Does

Keeps an always-current record of every employee's 3-month probation by:

1. **Recalculating** each employee's probation-end date, days left/overdue, and status.
2. **Detecting new joiners** from Gmail (Welcome / Day-01 emails) and adding them
   **under the correct joining-month section**, matching the sheet's exact formatting.
3. **Flagging** employees whose probation has completed or is ending soon, for HR action.

The engine is a single script: **`lunar_agent.py`** (an agent nicknamed *Lunar*).
It runs automatically Mon–Fri at 9:30 AM PKT and can also be run manually any time.

---

## 2. Quick Reference

| Item | Value |
|------|-------|
| **Trigger phrases** | "probation", "track probation", "probation status", "update probation tracker", "days left probation" |
| **Engine script** | `lunar_agent.py` |
| **Sheet** | Probation Tracker — `SPREADSHEET_ID = 1_yvL_lM3WzE5BBzsk60PO7gutsYer_y1PSFbTT0hJBY` |
| **Sheet tab GID** | `322356645` (tab title: "Probation Tracker") |
| **Probation period** | Exactly **3 calendar months** from joining date |
| **Schedule** | Mon–Fri 9:30 AM PKT via Windows Task Scheduler (`run_lunar.bat`) |
| **APIs needed** | Gmail (read) + Google Sheets (read/write) |
| **Approval** | **Always preview with `--dry-run` and get approval before writing** |
| **State file** | `lunar_state.json` (last-run date + known employees) |
| **Logs** | `logs/lunar_YYYY-MM-DD.log` |

---

## 3. Sheet Anatomy (must be matched exactly)

### 3.1 Layout
- **Row 1** — Title (the script rewrites it with the run date).
- **Row 2** — Cross-check note (manual).
- **Row 3** — Column header.
- **Then:** employees grouped under **month sections** in chronological order.

### 3.2 Month sections
Every employee sits under a header row labelled **`<Month YYYY> Joiners`**
(e.g. `April 2026 Joiners`), ordered by **joining month**. A new joiner goes under
their joining-month section; if that section doesn't exist yet, it is **created in the
correct chronological position**.

### 3.3 The 13 columns (A–M)
| Col | Field | Filled by | Notes |
|-----|-------|-----------|-------|
| A | # (serial) | Auto | Renumbered 1..N on every change |
| B | Name | Detection / HR | Full name |
| C | Designation | Detection / HR | From email subject if available |
| D | Department | **HR** | Left blank on auto-add — not in emails |
| E | Entity | **HR** | Left blank on auto-add — not in emails |
| F | Date of Joining | Detection / HR | Format **`DD Mon YYYY`** (e.g. `06 May 2026`) |
| G | Probation End Date | Auto | = F + 3 calendar months |
| H | Days Left / Overdue | Auto | e.g. `14 days` or `-25 days` |
| I | Status | Auto | See status labels below |
| J | Contract on Record | Detection / HR | Welcome/offer email subject, or "Welcome email on record" |
| K | Contract Date | **HR** | Left blank on auto-add — do NOT fabricate |
| L | Probation Closure Status | Auto / HR | `Not sent — due DD Mon YYYY` while pending; `Completed — Mon DD` when closed |
| M | Requirement | **HR** | `Needed` / `Not Needed` — left blank on auto-add |

> ⚠️ Columns **D, E, K, M** require human knowledge. On auto-add they are left **blank**
> for HR to fill — never guess or fabricate them.

### 3.4 Formatting spec (replicate when creating a new section header)
- **Section header row:** merged across **A:M**, background **RGB (0.84, 0.86, 0.89)**
  (light grey-blue), **bold**, font size 10, left-aligned.
- **Data rows:** no fill, not bold, size 10, centered.
- **How to create one in code:** insert a blank row → `copyPaste` with
  `pasteType: PASTE_FORMAT` from an existing header row → `mergeCells` A:M → write the label.

### 3.5 Dates
- Always **`DD Mon YYYY`** (`06 May 2026`). Never ISO (`2026-05-06`).

---

## 4. Probation Rules

### Rule 1 — Duration
Probation End Date = **Date of Joining + 3 calendar months** (use
`dateutil.relativedelta`, NOT "90 days"). Example: `15 Oct 2025` → `15 Jan 2026`.

### Rule 2 — Status labels (exact strings produced by the engine)
| Condition (days until probation end) | Status |
|---|---|
| > 60 days left | `In 1st Month` |
| 31–60 days left | `In 2nd Month — Upcoming` |
| 1–30 days left | `In 3rd Month — Ending Soon` |
| 0 days | `Probation Ends TODAY` |
| past end date | `Completed — Xd overdue` |

### Rule 3 — Sheet update safety
- **Dry-run first** (`--dry-run`) — preview, never write blind.
- **Approval required** before any live write.
- **Never delete rows.** Only update cells or insert new rows.
- **Recalc is written BEFORE inserting new joiners** (inserts shift row numbers, and
  recalc updates are keyed by absolute row number).
- **Log every run** to `logs/`.

### Rule 4 — State tracking
`lunar_state.json` records the last-run date and known employees, preventing duplicate work.

### Rule 5 — Gmail is READ-ONLY
Only search Gmail; never modify, label, or send. New joiners flow Gmail → sheet, one way.

---

## 5. New-Joiner Detection (how Gmail becomes a row)

1. **Search queries** (both `from:me`, last 120 days):
   - `subject:"What to Expect on Your Day 01"`
   - `subject:"Welcome to Taleemabad"`
2. **Why Welcome/Day-01 and not offer-letter stage:** people can decline after an offer.
   Keying off the Welcome/Day-01 email means only people who actually start get added —
   this avoids polluting the tracker with no-shows.
3. **Name** — taken from the `To:` header first (most reliable full name), then the
   subject `| Name` pattern, then the body greeting (`Hi <Name>,`).
4. **Joining date** — parsed from the body (`starting from <date>`, `joining date is <date>`,
   etc.). Supports `01 Oct 2025`, `01-Oct-2025`, `2025-10-01`, `01/10/2025`,
   `October 1, 2025`, `01 October 2025`.
5. **Designation** — extracted from the subject when present.
6. **Guards (skip if any true):**
   - Joining date older than 120 days (assumed already tracked)
   - Single-word names (too ambiguous to auto-add)
   - The HR manager's own name
   - Word-overlap match against an existing sheet name (dedup)
   - On the **exclusion lists** (see §6)
7. **Insertion** — the new row is placed under its joining-month section (header created if
   missing) with template formatting, then all serials are renumbered.

---

## 6. Exclusions (people who must NEVER be auto-added)

Some people are deliberately kept out of the tracker (tracked elsewhere, or their offer
fell through). These live in `lunar_agent.py` as:

- **`EXCLUDED_EMAILS`** — exact recipient addresses to skip.
- **`EXCLUDED_NAMES`** — full names to skip (case-insensitive).
- **`EXCLUDED_SUBJECT_KEYWORDS`** — e.g. `"audio monitoring"` skips an entire team even if
  new addresses appear.

**Currently excluded:**
- Audio Monitoring Officer (Assessments) team — 6 people (tracked separately by HR).
- Offers that fell through: **Muhammad Ahmed** (`muhammadfgs7@gmail.com`),
  **Raiyaan Hamid** (`raiyaanjhamid@gmail.com`).

**To exclude someone new:** add their email to `EXCLUDED_EMAILS` (and optionally their full
name to `EXCLUDED_NAMES`). To exclude a whole team, add a phrase to `EXCLUDED_SUBJECT_KEYWORDS`.

---

## 7. Step-by-Step Process (what one run does)

```
[Mon–Fri 9:30 AM PKT]  OR  [User: "update probation tracker"]
  ↓
1. Connect to Google (Gmail + Sheets) via token.json
2. Locate the "Probation Tracker" tab (gid 322356645)
3. Read all rows; identify data rows (col A is a number)
4. RECALCULATE every employee:
      G = joining + 3 months
      H = days left / overdue
      I = status label (Rule 2)
5. WRITE the recalculated G/H/I to the sheet   ← done BEFORE step 7
6. SCAN Gmail for new joiners (§5), applying all guards + exclusions (§6)
7. INSERT each new joiner under its month section (create header if missing,
      copy header formatting, leave D/E/K/M blank), then RENUMBER serials 1..N
8. Update the title row (row 1) with today's date
9. Save lunar_state.json (last-run date + known employees)
10. Write a run log to logs/lunar_YYYY-MM-DD.log
```

---

## 8. Commands

```bash
# Preview changes WITHOUT writing (always do this first)
python lunar_agent.py --dry-run

# Apply changes live (after approval)
python lunar_agent.py

# Check the scheduled task exists
powershell -Command "Get-ScheduledTask -TaskName 'Lunar - Probation Tracker'"

# See last/next scheduled run
powershell -Command "Get-ScheduledTask -TaskName 'Lunar - Probation Tracker' | Get-ScheduledTaskInfo | Select NextRunTime, LastRunTime, LastTaskResult"
```

---

## 9. Manual Run — Exact Procedure (with approval gate)

1. **Preview:** `python lunar_agent.py --dry-run`
2. **Review the preview** and show the user:
   - New joiners to be added (name, joining date, target month section)
   - Employees newly completed / overdue / ending soon
3. **Get explicit approval:** "Apply these changes? [Y/N]"
4. **Apply:** `python lunar_agent.py`
5. **Verify** (see §10) and report the summary.

---

## 10. Verification Checklist (after a live run)

- [ ] Title row shows today's date.
- [ ] Spot-check 3–4 employees: does G = F + 3 months, and H/I match today's date?
- [ ] Any new joiner is under the **correct month section**, with the **header formatted**
      (merged A:M, grey-blue, bold) and **D/E/K/M blank** for HR.
- [ ] Serials run 1..N with no gaps.
- [ ] No excluded person was added.
- [ ] A log file exists in `logs/`.

---

## 11. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `invalid_scope: Bad Request` on connect | `token.json` was granted fewer scopes than requested | The code loads the token with its **own granted scopes** so refresh succeeds. If it still fails, re-auth: delete `token.json`, run `python lunar_agent.py`, complete the browser sign-in once. |
| Token expired | Access token old | A valid refresh token auto-refreshes. If broken, re-auth as above. |
| New joiner not detected | Joining date missing/odd in email body, or single-word name | Ensure the Welcome/Day-01 email states the joining date clearly. |
| Same person detected twice | Spelling variants slipped past dedup | Add their email to `EXCLUDED_EMAILS` or fix the source email. |
| Row added at the bottom instead of a month section | Sheet structure not parsed (guard tripped) | The engine refuses to write if it can't parse the template; check rows 1–3 / header. |

---

## 12. Key Files

| File | Purpose |
|---|---|
| `lunar_agent.py` | The engine — all detection, recalculation, and insertion logic |
| `run_lunar.bat` | Launcher used by Windows Task Scheduler |
| `lunar_state.json` | Last-run date + known employees |
| `logs/lunar_YYYY-MM-DD.log` | Per-run log |
| `hr_assistant/config.py` | Google auth (scope must include `spreadsheets`, not readonly) |

**Relevant code in `lunar_agent.py`:** `calc_status`, `scan_gmail_for_new_joiners`,
`build_sheet_model`, `plan_joiner_insert`, `insert_joiners_matching_template`,
`renumber_serials`.

---

## 13. Example Run Summary

```
✓ Probation tracker updated — 2026-06-10
  Employees recalculated : 27
  New joiners added      : 1  (Sara Khan → "June 2026 Joiners")
  Completed / overdue    : Bibi Raheela (1d), Shoaib ud Din (15d), Fakhr Ul Islam (16d)
  Ending soon (<30d)     : Mehwish Bibi (14d), Zeest Hassan Qureshi (27d)
  Title row              : refreshed with run date
  Log                    : logs/lunar_2026-06-10.log
  Needs HR input         : Sara Khan — Department, Entity, Contract Date, Requirement
```

---

**Skill status:** ✅ Active  ·  **Automation:** Mon–Fri 9:30 AM PKT  ·
**Integration:** Gmail (read) + Google Sheets (read/write)  ·
**Approval:** Always preview before writing  ·  **Data safety:** Git-backed, never deletes rows
