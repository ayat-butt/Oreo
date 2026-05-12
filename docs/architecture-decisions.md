# Architecture Decisions

**Purpose:** Record major technical decisions and their rationale  
**Last updated:** 2026-05-12

## AD-001: Progressive Disclosure Context (3-Level Architecture)

**Decision:** Implement Level 1 (root) → Level 2 (subdirs) → Level 3 (.claude/) hierarchy  
**Status:** ✅ Active  
**Rationale:** Token efficiency, clearer navigation, reduced startup bloat  
**See:** [.claude/architecture/progressive-disclosure.md](../.claude/architecture/progressive-disclosure.md)

## AD-002: Google Sheets Access via Direct API (fetch_sheets_data.py)

**Decision:** Use Google Sheets API v4 directly, NOT MCP Google Drive wrapper  
**Status:** ✅ Active (colleague-validated)  
**Rationale:** MCP wrapper lacked permissions/didn't understand sheet structure. Direct API works reliably.  
**Implementation:** Python script using token.json authentication  
**See:** [sheet-operations.md](sheet-operations.md)

## AD-003: Payroll Isolation Keyword Trigger

**Decision:** Keyword "PAYROLL" triggers complete context switch to payroll/ folder  
**Status:** ✅ Active  
**Rationale:** Zero-tolerance for errors (affects real salaries), complex protocols, monthly rhythm  
**Scope:** Overrides all other context rules  
**See:** [.claude/rules/payroll-isolation.md](../.claude/rules/payroll-isolation.md)

## AD-004: Approval Gate on All Write Operations

**Decision:** Every email/calendar/document operation requires preview + approval first  
**Status:** ✅ Active  
**Rationale:** Prevents accidental sends, ensures quality, builds trust  
**Applies to:**
- Email drafting & sending
- Calendar event creation
- Document generation
- Teams messages
- Sheet modifications

## AD-005: Read-Only Markaz Database Access

**Decision:** Never write to Markaz. Read-only only.  
**Status:** ✅ Active  
**Rationale:** Markaz is source of truth for employee records. Corruption risk too high.  
**Implementation:** markaz_service.py has no write methods  
**See:** [memory/feedback_markaz_readonly.md](../memory/feedback_markaz_readonly.md)

## AD-006: Archive Old Scripts at 92% Token Reduction

**Decision:** Move 140+ old scripts to archive/ folder  
**Status:** ✅ Complete (2026-05-12)  
**Rationale:** Scripts were from old projects (tax, coordinates, insurance, hierarchy). Causing token bloat.  
**Result:** 273 → ~50 files in root, 1.5 MB freed  
**See:** [memory/project_structure_cleanup.md](../memory/project_structure_cleanup.md)

## AD-007: Script Evaluation Framework

**Decision:** Keep only 5 Python scripts in root: main.py, fetch_sheets_data.py, draft_contract.py, lunar_agent.py, send_email.py  
**Status:** ✅ Active  
**Rationale:** Essential workflows only. All else goes to archive or subdirectories.  
**Impact:** Reduces cognitive load, improves startup time

## AD-008: Payroll Formulas (EXACT, Non-Negotiable)

**Decision:** 7 mandatory formulas in exact order, no variations allowed  
**Status:** ✅ Critical  
**Rationale:** Any deviation affects salary calculations  
**Formulas:**
```
Basic = Gross × 90%
Medical = Basic × 10%
Other = Gross - Basic - Medical
Total Allow = sum
Taxable = TotalAllow - Medical - Unpaid
Deduct = all 8 items
Net = Allow - Deduct
```
**See:** [payroll/CLAUDE.md](../payroll/CLAUDE.md) + payroll/memory.md

## Pending Decisions

| Decision | Status | Notes |
|----------|--------|-------|
| Microsoft Teams integration | ⬜ Pending | Blocked by Anthropic key |
| Multi-user concurrent access | ❓ Undecided | Single-user assumption |
| Audit log retention policy | ❓ Undecided | Currently logs everything |
| Markaz sync frequency | ❓ Undecided | Currently on-demand read |

---

**Review schedule:** Quarterly  
**Last review:** 2026-05-12  
**See also:** .claude/architecture/ folder for detailed docs
