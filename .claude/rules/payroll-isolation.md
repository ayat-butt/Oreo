# Rule: Payroll Isolation

**Scope:** Entire project  
**Trigger:** Keyword "PAYROLL" in user message  
**Priority:** CRITICAL

## The Rule

When the user mentions "payroll" (case-insensitive):

1. **Immediate:** Switch ALL context to payroll/ folder
2. **Load:** payroll/CLAUDE.md (this overrides root CLAUDE.md)
3. **Use:** payroll/SESSIONS.md for progress (not root SESSIONS.md)
4. **Use:** payroll/memory.md (not root memory/)
5. **Write:** All outputs to payroll/output/ folder
6. **Never:** Reference or switch to contracts/onboarding/HR work

## Why This Rule Exists

Payroll is complex with zero-tolerance requirements:
- One wrong entry = affects someone's actual salary
- Mandatory protocols exist for verification, approval, calculations
- Monthly rhythm requires consistency
- Isolated working prevents cross-contamination with other HR workflows

## What Payroll Isolation Means

| Resource | Normal Mode | Payroll Mode |
|----------|-------------|--------------|
| CLAUDE.md | root/CLAUDE.md | payroll/CLAUDE.md |
| SESSIONS.md | root/SESSIONS.md | payroll/SESSIONS.md |
| memory.md | memory/MEMORY.md | payroll/memory.md |
| output folder | output/ | payroll/output/ |
| Context | All docs/ | payroll docs/ only |
| Rules | Global rules | payroll-specific rules |

## How to Recognize Payroll Work

User says:
- "payroll"
- "salary processing"
- "April payroll"
- "employee payment"
- "tax deduction"
- "pending dues"
- "overtime approval"

→ **Switch to payroll isolation immediately**

## Ending Payroll Mode

Payroll mode ends when:
- User switches topic away from payroll
- Payroll session is complete (documented in SESSIONS.md)
- User explicitly says "exit payroll mode"

Then return to normal mode and use root CLAUDE.md.

---

**Last updated:** 2026-05-12  
**Memory reference:** memory/feedback_payroll_always_separate.md
