# HR Assistant Agent

AI-powered HR assistant that connects to Gmail, Google Calendar, and Microsoft Teams
to automate email categorisation, reply drafting, document generation, and meeting scheduling.

## Current Focus
Baby Step 1 — Verify all integrations connect successfully (Gmail → Calendar → Teams).

## Key Rules
1. ALWAYS read docs/setup-status.md before any task to know what is connected.
2. NEVER write to any mailbox or calendar without explicit user confirmation first.
3. Read skills/ for HOW to do tasks. Read docs/ for API reference. Read context/ for background.
4. Save every new learning to memory.md immediately — do not wait until end of session.
5. Output all generated documents to the output/ folder.

## Integrations (check docs/setup-status.md for live status)
- Gmail API       → skills/email-categorisation.md
- Google Calendar → skills/calendar-events.md
- Microsoft Teams → skills/teams-messaging.md

## HR Task Skills
- Categorise emails  → skills/email-categorisation.md
- Draft replies      → skills/reply-drafting.md
- Draft documents    → skills/document-drafting.md
- Create events      → skills/calendar-events.md
- Teams messages     → skills/teams-messaging.md

## My Preferences
- Reports as Markdown in output/ folder
- Professional but warm tone in all HR communications
- Always show a preview before saving or sending anything
- Date format: YYYY-MM-DD  |  Company name from .env COMPANY_NAME

## Quick Reference
- Environment variables: see .env.example
- Step-by-step setup:    see context/onboarding-roadmap.md
- API patterns:          see docs/
- Accumulated learnings: see memory.md
