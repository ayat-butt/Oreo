# Master Skills Registry — All 7 Skills

**Status:** ACTIVE | **Last Updated:** 2026-05-12 | **All Rules Locked**

---

## Quick Navigation

| # | Skill | Trigger | Input Files | Output | Status |
|---|-------|---------|-------------|--------|--------|
| 1 | Email Categorisation | "categorize email" | 4 files | output/email/categorised/ | ✅ Connected |
| 2 | Reply Drafting | "draft reply" | 5 files | output/replies/ | ✅ Connected |
| 3 | Document Drafting | "draft contract" | 8 files | output/documents/contracts/ | ✅ Connected |
| 4 | Calendar Events | "schedule meeting" | 4 files | output/calendar/ | ✅ Connected |
| 5 | Teams Messaging | "send to teams" | 4 files | output/teams/ | ⬜ Pending |
| 6 | Probation Tracking | "probation" / "track probation" | 1 script | output/probation/ | ✅ Connected |
| 7 | Payroll Processing | "payroll" / "salary processing" | 1 isolated folder | payroll/output/ | ✅ Connected (ISOLATED) |

---

## All 7 Skills Detailed Below

See individual skill files for complete rules and regulations:

1. [skills/1-email-categorisation.md](1-email-categorisation.md)
2. [skills/2-reply-drafting.md](2-reply-drafting.md)
3. [skills/3-document-drafting.md](3-document-drafting.md)
4. [skills/4-calendar-events.md](4-calendar-events.md)
5. [skills/5-teams-messaging.md](5-teams-messaging.md)
6. [skills/6-probation-tracking.md](6-probation-tracking.md)
7. [skills/7-payroll-processing.md](7-payroll-processing.md)

---

## Global Rules (Apply to ALL Skills)

### 🎯 Core Quality Assurance
- **READ COMPLETELY** — Verify grammar, formatting, cross-check before ANYTHING
- **ALWAYS PREVIEW** — Never send/save without user approval
- **SAVE LEARNINGS** — Update memory after every discovery
- **OUTPUT ORGANIZED** — All results → skill-based output folder
- **CHECK INTEGRATIONS FIRST** — Read docs/setup-status.md before any work

### 🔐 Data Protection
- **ZERO Data Loss** — All changes git-backed, rollback available
- **ARCHIVE Preserved** — Legacy files in output/archive/
- **Markaz Read-Only** — NEVER write/modify/delete in Markaz DB
- **No Hallucination** — Only load declared input files

### ✅ Approval & Verification
- **Preview Always** — Show user preview before any action
- **Explicit Approval** — Get [S]ave/[D]iscard confirmation
- **No Auto-Send** — Save as draft first, never send directly
- **Logging Required** — Log results with timestamp

### 🔄 Context & Memory
- **Progressive Disclosure** — Load context hierarchically
- **Session Logging** — Log commands to memory/session_log.md
- **Memory Updates** — Save rules to memory/feedback_*.md
- **CLAUDE.md Navigation** — Use hierarchy for context switching

---

## Integration Status (CRITICAL)

**Last Verified:** 2026-05-12

| Integration | Status | Connected | Key File |
|-------------|--------|-----------|----------|
| Gmail API | ✅ Connected | Yes | token.json |
| Google Calendar API | ✅ Connected | Yes | token.json (shared) |
| Google Drive API | ✅ Connected | Yes | token.json (shared) |
| Anthropic Claude | ⬜ Pending | No | .env (ANTHROPIC_API_KEY empty) |
| Microsoft Teams | ⬜ Pending | No | Needs Anthropic key first |
| Markaz DB | ✅ Connected (Read-Only) | Yes | MARKAZ_DB_URL in .env |
| Google Sheets API | ✅ Connected | Yes | fetch_sheets_data.py + token.json |

**Action Required:** Add ANTHROPIC_API_KEY to .env to unlock Teams and all AI features.

---

## Skill Isolation Rules

### Payroll Isolation (CRITICAL)
**Trigger:** Keyword "PAYROLL" anywhere in message
- **Switch Context:** → payroll/ folder ONLY
- **Load:** payroll/CLAUDE.md (overrides root)
- **Use:** payroll/memory.md, payroll/SESSIONS.md
- **Write:** payroll/output/ folder
- **Never merge** with other HR work

### Probation Isolation (Medium Priority)
**Trigger:** Keyword "PROBATION" or "TRACK PROBATION"
- **Use:** lunar_agent.py (automatic daily runs)
- **Sheet:** Probation Tracker Google Sheet (SPREADSHEET_ID in script)
- **Output:** output/probation/[YYYY-MM-DD]/
- **Read-Only on Gmail:** Search only, never modify

### Other Skills (No Isolation)
- Email, Reply, Document, Calendar, Teams use normal context
- Can reference each other (e.g., calendar invites linked to onboarding)

---

## How to Use This Registry

When user triggers a skill:

1. **Identify skill** from trigger phrase table above
2. **Load skill file** from skills/ folder (e.g., skills/1-email-categorisation.md)
3. **Read ALL rules** in that file (input files, execution flow, common mistakes)
4. **Check integration status** — if not connected, inform user
5. **Execute with full rules locked in** — no shortcuts, no variations
6. **Log results** with timestamp to output folder
7. **Update memory** if new patterns discovered

---

## Emergency Protocols

### If Integration Fails
- Check docs/setup-status.md for status
- Read error logs in logs/ folder
- Email support: HR_MANAGER_EMAIL from .env

### If Data Corruption Suspected
- Git checkout to v1.0-before-optimization tag
- All legacy files in output/archive/
- 5-second rollback available

### If Markaz Fails
- Script uses read-only connection only
- Verify MARKAZ_DB_URL in .env
- Check PostgreSQL connectivity
- Never attempt write — report to admin

---

**Framework Status:** ✅ LIVE & PRODUCTION READY  
**All Rules:** LOCKED & ENFORCEABLE  
**Data Safety:** GUARANTEED with git-backing  
**Next Step:** Verify Anthropic API key and check all integrations
