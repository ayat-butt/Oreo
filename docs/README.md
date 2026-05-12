# Documentation Index

## Quick Start

1. **First time?** → Read [setup-status.md](setup-status.md)
2. **Need API details?** → See [api-reference/](api-reference/)
3. **Architectural decisions?** → See [architecture-decisions.md](architecture-decisions.md)
4. **Sheet operations?** → See [sheet-operations.md](sheet-operations.md)

## File Organization

### Operational (Check first)
- **[setup-status.md](setup-status.md)** — Live integration status (Gmail, Calendar, Drive, Teams)
  - Update when adding/fixing integrations
  - 22 lines, always current

### How-To Guides
- **[sheet-operations.md](sheet-operations.md)** — How to read any Google Sheet
  - Primary script: fetch_sheets_data.py
  - Usage examples, troubleshooting
  - Colleague-validated approach
- **More guides:** See subdirectories below

### Architecture & Decisions
- **[architecture-decisions.md](architecture-decisions.md)** — Why we made certain technical choices
  - Progressive disclosure (3-level context)
  - Google Sheets API vs MCP
  - Payroll isolation keyword
  - Approval gate on writes
  - 94 lines, comprehensive

### API Reference (Context-specific)
- **[api-reference/gmail.md](api-reference/gmail.md)** — Gmail API patterns
- **[api-reference/teams.md](api-reference/teams.md)** — Teams API patterns
- More: See api-reference/ folder

## Documentation Structure

```
docs/
├── README.md ..................... (this file)
├── setup-status.md ............... Live integration status
├── sheet-operations.md ........... Google Sheets guide
├── architecture-decisions.md ..... Technical decisions
└── api-reference/
    ├── gmail.md .................. Gmail API reference
    └── teams.md .................. Teams API reference
```

## When to Add New Docs

**Create a new doc if:**
- New integration is added
- New workflow is documented
- Major decision is made
- How-to guide for common task

**Update existing doc if:**
- Integration status changes
- API details change
- Decision is revisited

**Add to archive if:**
- Doc is obsolete
- Info moved elsewhere
- Approach changed

## Doc Standards

- **All docs:** YYYY-MM-DD dates
- **API docs:** Include code examples
- **Guides:** Step-by-step numbered
- **Decisions:** Include rationale (the WHY)
- **Length:** Keep under 100 lines if possible

---

**Last updated:** 2026-05-12  
**Total docs:** 5 primary + architecture folder  
**See also:** root [CLAUDE.md](../CLAUDE.md) for navigation
