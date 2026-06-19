# HR Assistant Agent

AI-powered HR assistant that connects to Gmail, Google Calendar, and Microsoft Teams
to automate email categorization, reply drafting, document generation, and meeting scheduling.

## What This Is
- **Project:** HR automation framework with Google Workspace + Claude integration
- **Status:** Active — Gmail/Calendar/Drive connected, Teams pending
- **Focus:** Onboarding, contracts, payroll, probation tracking, email management

## How to Use This CLAUDE.md

**Level 1 (You are here):** Project overview and navigation  
**Level 2 (Subdirectories):** Context-specific rules for hr_assistant/, payroll/, skills/  
**Level 3 (.claude/ folder):** Detailed rules and skill triggers  
**Live status:** Check docs/setup-status.md before any integration task

## Key Commands

```bash
python main.py                    # Run HR assistant
python fetch_sheets_data.py       # Read any Google Sheet
python lunar_agent.py             # Run probation tracker (Mon-Fri 9:30 AM)
python draft_contract.py          # Draft onboarding contracts
```

## Global Rules

1. **Always preview before sending:** Preview emails, calendar invites, and document changes
2. **Save learnings immediately:** Update memory.md after every non-trivial discovery
3. **Output reports to output/:** All generated documents → output/ folder
4. **Read integration status first:** Check docs/setup-status.md for what's connected
5. **Payroll is isolated:** Keyword "PAYROLL" triggers complete isolation → payroll/ folder only

## Navigation

| Need | Go To | Load |
|------|-------|------|
| Email automation | [skills/email-categorisation.md](skills/email-categorisation.md) | When working with Gmail |
| Draft documents | [hr_assistant/CLAUDE.md](hr_assistant/CLAUDE.md) | When creating contracts/emails |
| Payroll operations | [payroll/CLAUDE.md](payroll/CLAUDE.md) | When keyword "PAYROLL" appears |
| Sheet operations | [docs/sheet-operations.md](docs/sheet-operations.md) | When reading/writing Google Sheets |
| API patterns | [docs/](docs/) | For integration details |
| Project learnings | [memory.md](memory.md) | Persistent knowledge across sessions |

## Code Style

- Python: Follow PEP 8, type hints, clear variable names
- Markdown: H1 = file title, H2 = sections, lists for steps
- Dates: YYYY-MM-DD format always
- Company info: Load from .env COMPANY_NAME

---
**Last updated:** 2026-05-12  
**See also:** [Project Structure & Token Optimization](memory.md)
