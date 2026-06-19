# Documentation Audit Report & Progressive Disclosure Refactoring Plan
**Date**: 2026-05-07  
**Status**: AUDIT COMPLETE — Ready for Implementation

---

## PART 1: CURRENT STATE ANALYSIS

### Directory Structure (Current)
```
C:\Agent Oreo/
├── CLAUDE.md                          ← Root (39 lines) — GOOD SIZE
├── docs/
│   ├── setup-status.md               (23 lines) — integration status tracker
│   ├── gmail-api-reference.md        (?) — API reference
│   └── teams-api-reference.md        (?) — API reference
├── context/
│   ├── onboarding-roadmap.md         (100+ lines) — baby steps for setup
│   └── project-background.md         (28 lines) — project overview
├── skills/                            ← 5 HR task skill files
│   ├── email-categorisation.md
│   ├── reply-drafting.md
│   ├── document-drafting.md
│   ├── calendar-events.md
│   └── teams-messaging.md
├── .claude/
│   ├── settings.json                 ← Permissions & MCP config
│   └── settings.local.json           ← User-level overrides
└── payroll/                           ← SUBDIRECTORY WITH OWN CONTEXT
    ├── context/
    │   └── payroll-procedures.md
    ├── docs/
    │   ├── payroll-api-reference.md
    │   ├── payroll-formulas-reference.md
    │   ├── payroll-processing-checklist.md
    │   └── payroll-workflow-summary.md
    ├── skills/
    │   ├── PAYROLL_REGISTRY.md
    │   ├── income-tax-calculation.md
    │   └── salary-docs.md
    ├── memory.md                     ← Payroll-specific memory
    ├── SESSIONS.md                   ← Session tracking
    ├── CHAT_LOG.md
    ├── MONDAY_SESSION_PLAN.md
    └── output/                       ← Generated payroll reports
```

---

## PART 2: AUDIT FINDINGS

### ✅ What's Working Well
1. **Root CLAUDE.md is appropriately sized** (39 lines) — concise, pointers to deeper docs
2. **Payroll has its own isolated context** — correct use of subdirectory CLAUDE.md pattern
3. **Integration status tracked** in docs/setup-status.md — single source of truth
4. **Skills are organized by task** — clear mapping to what they do

### ⚠️ Problems Identified

#### Problem 1: Token Bloat in Root Context
- **onboarding-roadmap.md** (100+ lines) is **task-specific setup** — should move to Level 3
- **Context files in /context are loaded even when not relevant**
  - Example: User doing payroll work loads "project-background.md" which is about HR onboarding
  - This is wasted tokens

#### Problem 2: Missing Progressive Disclosure Tiers
- No explicit Level 2 (subdirectory CLAUDE.md) files except payroll
- No explicit Level 3 (skill-specific rules) structure
- Current system loads everything in /context and /docs regardless of task

#### Problem 3: Documentation Redundancy
- **payroll/docs/** has 4 separate files that could be consolidated
  - payroll-formulas-reference.md
  - payroll-processing-checklist.md
  - payroll-workflow-summary.md
  - payroll-api-reference.md
- **No clear distinction** between "reference" (API) vs "procedure" (workflow) vs "rules" (formulas)

#### Problem 4: Memory File Fragmentation
- **Root memory.md** — for general HR learnings
- **payroll/memory.md** — for payroll-specific learnings
- These should not both load at root level when working outside payroll

#### Problem 5: Session Tracking Unclear
- **payroll/SESSIONS.md** — session log
- **payroll/CHAT_LOG.md** — appears to be chat transcript?
- **payroll/MONDAY_SESSION_PLAN.md** — session plan?
- Unclear purpose and when each is used

---

## PART 3: PROGRESSIVE DISCLOSURE ARCHITECTURE (Proposed)

### Level 1: ROOT CLAUDE.md (Under 150 Lines)
**Purpose**: Agent's north star — project overview + command index

```
Root CLAUDE.md should contain:
├── Project overview (WHAT/WHY)
├── 3-4 key commands (build, test, deploy)
├── Code style rules (brief)
├── Integration status (pointer to docs/setup-status.md)
├── Top-level rules (approval, previews, confirmations)
└── POINTERS to Level 2 & 3 (not embedded)
```

**Current root CLAUDE.md**: ✅ Adequate (39 lines)
**Action**: Minor cleanup — move HR task details to Level 2

---

### Level 2: Subdirectory CLAUDE.md (Context-Specific)
**Purpose**: When working IN a subdirectory, load only that context

#### Example: `payroll/CLAUDE.md` (NEW)
```
Should contain ONLY:
├── Payroll module overview
├── Key payroll commands
├── Payroll-specific rules (e.g., "ALWAYS verify employee 4-step", "formulas must be in exact order")
├── Pointer to payroll/docs/ (reference materials)
├── Pointer to payroll/memory.md (learnings)
└── Pointer to payroll/skills/ (specialized tasks)

Should NOT contain:
├── HR task details (those are in root)
├── setup instructions (those are in context/)
├── full API references (those are in docs/)
```

---

### Level 3: Skills & Rules (On-Demand)
**Purpose**: Load ONLY when the specific task is triggered

#### Example Structure:
```
.claude/rules/               ← Rules files (triggered by filename/keywords)
├── approval-rules.md        (when drafting/sending)
├── memory-rules.md          (when updating memory)
└── payroll-formulas.md      (when "payroll" keyword detected)

payroll/skills/
├── income-tax-calculation.md   (trigger: "calculate tax" / "April payroll")
├── salary-docs.md             (trigger: "salary slip" / "payroll document")
└── PAYROLL_REGISTRY.md        (trigger: "registry" / "reference")
```

---

## PART 4: RECOMMENDED FOLDER RESTRUCTURE

### New Structure:
```
C:\Agent Oreo/
│
├── CLAUDE.md                          ← Level 1: Root (50 lines max)
│
├── .claude/
│   ├── settings.json
│   ├── settings.local.json
│   └── rules/                         ← Level 3: Global rules
│       ├── approval-rules.md
│       ├── memory-update-rules.md
│       └── communication-style.md
│
├── docs/                              ← Level 1: Reference pointers only
│   ├── setup-status.md               (keep as-is)
│   ├── ARCHITECTURE.md               (NEW: system design)
│   └── API/                          (NEW: organize APIs by provider)
│       ├── gmail-api-reference.md
│       ├── calendar-api-reference.md
│       ├── teams-api-reference.md
│       └── sheets-api-reference.md
│
├── context/                           ← Level 1: Setup & background (optional at root)
│   ├── SETUP_ROADMAP.md              (moved from onboarding-roadmap.md)
│   └── PROJECT_VISION.md             (moved from project-background.md)
│
├── skills/                            ← Level 2: HR-specific skills
│   ├── email-categorisation.md
│   ├── reply-drafting.md
│   ├── document-drafting.md
│   ├── calendar-events.md
│   └── teams-messaging.md
│
├── memory.md                          ← Level 2: Auto-memory for HR learnings
│
├── output/                            ← Generated reports (HR)
│
├── payroll/                           ← SUBDIRECTORY: Complete isolation
│   ├── CLAUDE.md                      ← Level 2: Payroll-specific rules
│   │
│   ├── docs/
│   │   ├── PAYROLL_ARCHITECTURE.md   (NEW: consolidates all payroll knowledge)
│   │   └── API/
│   │       └── sheets-api.md
│   │
│   ├── .claude/
│   │   └── rules/
│   │       ├── formula-rules.md
│   │       ├── verification-rules.md
│   │       └── tax-rules.md
│   │
│   ├── skills/                       ← Level 3: Payroll-specific
│   │   ├── income-tax-calculation.md
│   │   ├── salary-processing.md
│   │   └── payroll-verification.md
│   │
│   ├── memory.md                     ← Level 2: Payroll-specific learnings
│   ├── SESSIONS.md                   ← Payroll session log
│   ├── output/                       ← Generated payroll reports
│   └── context/
│       └── PAYROLL_PROCEDURES.md
```

---

## PART 5: FILE CONSOLIDATION PLAN

### Consolidation 1: Payroll Docs
**Current State**: 4 separate files
```
payroll/docs/
├── payroll-api-reference.md
├── payroll-formulas-reference.md
├── payroll-processing-checklist.md
└── payroll-workflow-summary.md
```

**Proposed**: Single `PAYROLL_ARCHITECTURE.md`
```
PAYROLL_ARCHITECTURE.md (comprehensive)
├── Section 1: System overview
├── Section 2: Payroll workflow (what is processing-checklist → here)
├── Section 3: Key formulas (what is formulas-reference → here)
├── Section 4: API references (what is api-reference → here)
├── Section 5: Verification procedures (what is procedures → here)
└── Section 6: Decision tree (how to handle edge cases)
```

**Benefit**: Single 200-line reference vs 4 scattered files; easier to keep in sync

### Consolidation 2: Root Context Files
**Current State**: 2 separate files
```
context/
├── onboarding-roadmap.md  (100+ lines)
└── project-background.md  (28 lines)
```

**Proposed**: Split by purpose
```
context/
├── SETUP_ROADMAP.md        (baby steps — move to .claude/rules if not used often)
└── PROJECT_VISION.md       (why we built this, loaded once)
```

---

## PART 6: LEVEL 3 RULES — WHAT TO CREATE

### New Global Rules (.claude/rules/)

#### `approval-rules.md`
```
Trigger: When drafting/sending emails, contracts, calendar invites
Contains: 
- "Always preview before sending"
- "Get explicit confirmation for writes"
- "Review formatting before output"
```

#### `memory-update-rules.md`
```
Trigger: When saving to memory
Contains:
- "Save learnings immediately after task"
- "Distinguish user feedback vs project context vs learnings"
- "Use structured format: name, description, type"
```

#### `communication-style.md`
```
Trigger: When drafting HR communications
Contains:
- "Professional but warm tone"
- "Date format: YYYY-MM-DD"
- "Company name from COMPANY_NAME env var"
- "Sign as Oreo for agent-sent emails"
```

### New Payroll Rules (payroll/.claude/rules/)

#### `formula-rules.md`
```
Trigger: When calculating payroll
Contains:
- The 7 mandatory formulas (Basic, Medical, Other, etc.)
- EXACT order of execution
- Special cases (probation, part-time, increments)
```

#### `verification-rules.md`
```
Trigger: When processing employee data
Contains:
- 4-step employee verification (name → ID → entity → other details)
- Salary change alert protocol
- Pending dues protocol
```

#### `tax-rules.md`
```
Trigger: When calculating tax
Contains:
- FBR tax slabs
- YTD calculation rules
- April tax formula
```

---

## PART 7: IMPLEMENTATION CHECKLIST

### Phase 1: Consolidation (1 hour)
- [ ] Consolidate payroll/docs into PAYROLL_ARCHITECTURE.md
- [ ] Consolidate context files (SETUP_ROADMAP.md, PROJECT_VISION.md)
- [ ] Update payroll/SESSIONS.md header to clarify its purpose
- [ ] Delete redundant files

### Phase 2: Create Level 3 Rules (1.5 hours)
- [ ] Create .claude/rules/ directory
- [ ] Create global rules:
  - [ ] approval-rules.md
  - [ ] memory-update-rules.md
  - [ ] communication-style.md
- [ ] Create payroll/.claude/rules/:
  - [ ] formula-rules.md
  - [ ] verification-rules.md
  - [ ] tax-rules.md

### Phase 3: Create Subdirectory CLAUDE.md (30 min)
- [ ] Create payroll/CLAUDE.md (rules + pointers only)
- [ ] Update root CLAUDE.md (remove payroll-specific items)
- [ ] Remove redundant pointers

### Phase 4: Documentation (30 min)
- [ ] Update docs/ARCHITECTURE.md to explain new structure
- [ ] Add "How to Add Context" guide
- [ ] Update root CLAUDE.md with pointer to docs/ARCHITECTURE.md

### Phase 5: Memory Structure Update (30 min)
- [ ] Review payroll/memory.md — ensure it's payroll-only
- [ ] Review root memory.md — ensure it's HR-only
- [ ] Add rule to MEMORY.md index explaining what loads when

---

## PART 8: TOKEN SAVINGS ESTIMATE

### Current Setup (All Files Always Loaded)
- Root CLAUDE.md: 39 lines
- docs/setup-status.md: 23 lines
- context/onboarding-roadmap.md: 100+ lines ← BLOAT
- context/project-background.md: 28 lines
- memory.md: 3000+ lines (indexed) ← BLOAT
- **Total per session: ~3200 lines = ~900 tokens**

### Proposed Setup (Progressive Disclosure)
- Root CLAUDE.md: 50 lines (cleaned up)
- Memory index (MEMORY.md header): 50 lines (linked, not embedded)
- Task-specific rules: ~100 lines (loaded only when relevant)
- **Baseline: ~200 lines = ~50 tokens**
- **Per payroll session: +200 lines (payroll rules) = 100 extra tokens**

### Savings: **80-85% reduction** in root-level token bloat

---

## PART 9: QUICK START GUIDE FOR FUTURE USE

### When Adding New Context:

1. **Is it about how to do ONE task?**
   → Create a skill file in `skills/` with trigger description

2. **Is it about rules that apply globally?**
   → Create a rule file in `.claude/rules/` with trigger keywords

3. **Is it about a new module/subdirectory?**
   → Create `subdirectory/CLAUDE.md` (Level 2) + `subdirectory/.claude/rules/` (Level 3)

4. **Is it an API reference?**
   → Put in `docs/API/` — don't embed in CLAUDE.md

5. **Is it setup/onboarding?**
   → Put in `context/` — only load this once

---

## Summary

| Level | Purpose | Load When | Size |
|-------|---------|-----------|------|
| **Level 1: Root CLAUDE.md** | Project overview + command index | Always | <150 lines |
| **Level 2: Subdirectory CLAUDE.md** | Context-specific rules | When working in that directory | <100 lines each |
| **Level 2: skills/** | Task-specific how-tos | When relevant task detected | ~50 lines each |
| **Level 2: memory.md** | Learnings index | Always (index only) | <50 lines |
| **Level 3: .claude/rules/** | Global behavioral rules | When triggered by keywords | ~50 lines each |
| **Level 3: docs/** | API references, architecture | On-demand (pointer in CLAUDE.md) | Unlimited |

**Result**: Cleaner context window, faster Claude startup, easier for future agent iterations.

---

**Report Prepared By**: Oreo — Ayat's HR AI Assistant  
**Recommendation**: Proceed with Phase 1 & 2 immediately. Phases 3-5 can happen in parallel.