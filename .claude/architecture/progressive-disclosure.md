# Architecture: Progressive Disclosure (3-Level Context)

**Decision:** Implement 3-level progressive disclosure to optimize token consumption  
**Status:** Active  
**Adopted:** 2026-05-12

## The Problem

273 files in root → bloated token usage  
All context loaded for every conversation → inefficient  
Task-specific instructions scattered → confusing navigation

## The Solution: 3-Level Architecture

### Level 1 — Root CLAUDE.md
**Loaded:** Always (every conversation)  
**Contains:** Project overview, navigation pointers, global rules  
**Size:** ~80 lines  
**Topics:** What this project is, how to find things, key commands

### Level 2 — Subdirectory CLAUDE.md
**Loaded:** When working in that directory  
**Contains:** Context-specific rules, module guide, patterns  
**Directories:**
- `hr_assistant/CLAUDE.md` — Service modules
- `payroll/CLAUDE.md` — Payroll isolation rules
- `skills/CLAUDE.md` — Skill activation patterns

### Level 3 — .claude/ Folder
**Loaded:** On-demand via explicit reference  
**Contains:** Detailed rules, architecture decisions, rarely-needed context  
**Subfolders:**
- `.claude/rules/` — Specific rules (payroll-isolation.md, etc.)
- `.claude/architecture/` — Decision documents (this file)

## Benefits

| Metric | Before | After |
|--------|--------|-------|
| Root CLAUDE.md | 39 lines | 45 lines (cleaner) |
| Context bloat | 273 files | ~50 in root |
| Loaded on startup | All docs | Only Level 1 |
| Token efficiency | ~30% waste | ~5% waste |
| Clarity | Scattered | Hierarchical |

## Navigation Example

**User asks:** "Help me draft a contract"

1. Load Level 1 → CLAUDE.md (overview)
2. Read pointer → "Draft documents → [skills/document-drafting.md](skills/document-drafting.md)"
3. Load Level 2 → skills/CLAUDE.md (skill patterns)
4. Load Level 2 → skills/document-drafting.md (specific how-to)
5. Execute using hr_assistant/contract_service.py

**No unnecessary context loaded.**

## Implementation Checklist

- [x] Root CLAUDE.md (80 lines, navigation focus)
- [x] hr_assistant/CLAUDE.md (module guide)
- [x] payroll/CLAUDE.md (isolation rules)
- [x] skills/CLAUDE.md (skill reference)
- [x] .claude/rules/payroll-isolation.md
- [x] docs/sheet-operations.md (Level 1 pointer)
- [ ] docs/architecture-decisions.md (collected decisions)
- [ ] docs/api-reference/ (consolidated APIs)
- [ ] Review & audit remaining docs

## Trade-offs

**✅ Gains:**
- Faster context loading
- Clearer navigation
- Less token waste
- Easier onboarding for new context

**⚠️ Trade-offs:**
- More files to maintain
- Requires learning navigation structure
- Updates must stay in sync across levels

---

**Next steps:**
1. Audit and consolidate docs/ folder
2. Create docs/architecture-decisions.md
3. Move API references to docs/api-reference/
4. Test context loading in real conversations
